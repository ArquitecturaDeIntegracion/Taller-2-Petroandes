"""Ejecuta F8 en una copia de laboratorio y registra resultados por caso."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from pytest import MonkeyPatch

from f0_common import configure_cache, write_report
from f7_inspector import fixture_config, historical_lab
from f7_inspector_client import Inspector
from f8_judge import Judge
from f8_metrics import assess_case, section, summarize
from petroandes.compose import answer
from petroandes.contracts.documents import Fragment
from petroandes.deployment import LocalDeployment
from petroandes.index.publication import document_identity
from petroandes.mcp_tools import CONTRACTS
from project_paths import APP_ROOT

SUITE = APP_ROOT / "config/f8-prueba-tecnica.json"


def python_result(case, service):
    query_type, response_type, _ = CONTRACTS[case["herramienta"]]
    query = query_type.model_validate(case["entrada"])
    if case["herramienta"] == "buscar_documentos":
        report = answer(service, query)
    else:
        report = service.obtain(query)
    return response_type.model_validate(report["resultado"]), report["traza"]


def without_correlation(response):
    return response.model_dump(mode="json", exclude={"correlation_id"})


def collect_case(case, service, fragments, inspector, destination):
    label, tool = case["id"], case["herramienta"]
    case_dir = destination / label
    documents = {document_identity(doc) for doc in service.policy.eligible().documentos}
    eligible = {key: part for key, part in fragments.items() if document_identity(part) in documents}
    python, trace = python_result(case, service)
    write_report(case_dir / "python.json", {"entrada": case["entrada"],
                 "resultado": python.model_dump(mode="json")}, emit=False)
    write_report(case_dir / "traza.json", trace, emit=False)
    for branch, candidates in trace.get("candidatos", {}).items():
        sources = [{"chunk_id": key, "seccion": section(eligible[key]) if key in eligible else None,
                    "pdf_sha256": eligible[key].pdf_sha256 if key in eligible else None}
                   for key in candidates]
        for offset in range(0, len(sources), 15):
            write_report(case_dir / f"{branch}-{offset // 15 + 1}.json",
                         {"candidatos": sources[offset:offset + 15]}, emit=False)

    started = perf_counter()
    mcp, _ = inspector.run(f"{label}/inspector", case["contexto"], tool=tool, arguments=case["entrada"])
    transport_ms = (perf_counter() - started) * 1000
    if mcp.get("isError"):
        raise RuntimeError("MCP marcó la llamada como error")
    mcp_response = type(python).model_validate(mcp["structuredContent"])
    parity = without_correlation(python) == without_correlation(mcp_response)
    metadata = {"caso": case, "perfil": "laboratorio",
                "contexto_servicio": service.policy.context.model_dump(mode="json"),
                "instante_evaluacion": service.policy.clock().isoformat(),
                "estado_observado": python.estado, "revision_gobierno": python.revision_gobierno,
                "generation_id": python.generation_id, "paridad_mcp": parity,
                "ms_mcp_desde_lanzamiento": transport_ms,
                "esperaba_abstencion": case["esperado"]["estado"] == "abstencion"}
    return {"metadata": metadata, "respuesta": python.model_dump(mode="json"), "traza": trace,
            "fuentes_elegibles": {key: part.model_dump(mode="json") for key, part in eligible.items()}}


def run_cases(cases, workspace, historical, parts, inspector, destination):
    fragments = {key: Fragment.model_validate(part) for key, part in parts.items()}
    habitual = LocalDeployment("laboratorio")
    habitual.catalog_path = workspace / "despliegue/catalog/laboratorio/catalog.sqlite3"
    habitual.index = workspace / "despliegue/indexes/laboratorio"
    habitual.encoder = historical.encoder
    completed, failures = [], []
    with habitual.connect() as regular:
        for case in cases:
            service = {"historico": historical, "habitual": regular}[case["contexto"]]
            try:
                completed.append(collect_case(case, service, fragments, inspector, destination))
            except (OSError, RuntimeError, KeyError, ValueError) as exc:
                failure = {"id": case["id"], "tipo": type(exc).__name__, "motivo": str(exc)}
                write_report(destination / case["id"] / "error.json", failure, emit=False)
                failures.append(failure)
    return completed, failures


def collect(cases, destination, handoff):
    with TemporaryDirectory(prefix="petroandes-f8-") as directory, MonkeyPatch.context() as patch:
        workspace = Path(directory)
        with historical_lab(workspace, patch) as (service, parts):
            inspector = Inspector(workspace, destination)
            inspector.configure(fixture_config(workspace, service))
            records, failures = run_cases(cases, workspace, service, parts, inspector, destination)
    handoff.write_text(json.dumps({"inspector": inspector.version, "casos": records, "fallos": failures}),
                       encoding="utf-8")


def evaluate(records, judge, destination):
    completed = []
    for record in records:
        metadata, trace = record["metadata"], record["traza"]
        case = metadata["caso"]
        response = CONTRACTS[case["herramienta"]][1].model_validate(record["respuesta"])
        sources = {key: Fragment.model_validate(part) for key, part in record["fuentes_elegibles"].items()}
        observation = metadata | assess_case(case, response, trace, sources, judge)
        write_report(destination / case["id"] / "evaluacion.json", observation, emit=False)
        completed.append(observation)
    return completed


def review_inventory():
    statuses = Counter()
    for path in (APP_ROOT / "docs/revision/casos").glob("*.json"):
        proposal = json.loads(path.read_text(encoding="utf-8"))
        statuses[proposal["revision_humana"]["estado"]] += 1
    return dict(sorted(statuses.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--collect-to", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    destination = (APP_ROOT / args.output_dir).resolve()
    configure_cache(offline=True)
    raw = SUITE.read_bytes()
    suite = json.loads(raw)
    if args.collect_to:
        collect(suite["casos"], destination, args.collect_to)
        return 0
    destination.mkdir(parents=True, exist_ok=False)
    try:
        # El proceso que usa E5 y los hijos MCP termina antes de cargar laya.
        with TemporaryDirectory(prefix="petroandes-f8-traspaso-") as directory:
            handoff = Path(directory) / "captura.json"
            subprocess.run([sys.executable, __file__, "--output-dir", str(destination),
                            "--collect-to", str(handoff)], check=True)
            captured = json.loads(handoff.read_text(encoding="utf-8"))
        judge = Judge()
        completed = evaluate(captured["casos"], judge, destination)
    except (OSError, RuntimeError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        write_report(destination / "summary.json", {"status": "failed", "tipo": type(exc).__name__, "error": str(exc)})
        return 1

    checks = ("paridad_mcp", "resultado_esperado", "secciones_citadas_esperadas", "literales_esperados",
              "candidatos_elegibles")
    failures = captured["fallos"]
    metrics = summarize(completed)
    passed = (not failures and all(all(case[key] for key in checks) for case in completed)
              and metrics["procedencia"]["valor"] == 1
              and all(metrics[key]["denominador"] and not metrics[key]["errores"]
                      for key in ("anclaje_laya", "pertinencia_laya")))
    summary = {"status": "passed" if passed else "failed", "alcance": suite["alcance"],
               "suite_sha256": hashlib.sha256(raw).hexdigest(), "inspector": captured["inspector"],
               "plataforma": platform.platform(), "evaluador": judge.configuration,
               "casos_propuestos_por_estado": review_inventory(), "evaluacion_formal_ejecutada": False,
               "casos_intentados": len(suite["casos"]), "casos_con_resultado": len(completed), "fallos": failures,
               "casos": [{"id": case["caso"]["id"], "estado": case["estado_observado"],
                          **{key: case[key] for key in checks}} for case in completed],
               "metricas_diagnosticas": metrics}
    write_report(destination / "summary.json", summary)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
