"""Ensayo reproducible F9 con PDF, recuperación real, compositor e Inspector."""
import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import MonkeyPatch

from f0_common import configure_cache, write_report
from f7_inspector import DIRECT, SEARCH, historical_lab, validated, verify_list
from f7_inspector_client import Inspector, server_entry
from f9_observe import MARKER, observed, self_check
from f9_sources import DOCUMENT, PAYLOAD_MARKERS, SECTION, candidate_details, prepare_audit
from petroandes.catalog.api import Catalog
from petroandes.compose import answer
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.governance.eligibility import EligibilityService
from petroandes.index.common import context_data, file_digest
from petroandes.paths import APP_ROOT
from petroandes.retrieve import Retriever

ATTACK = SearchQuery(consulta="En COM-PRV-0134 localice el anexo de notas de integración.",
                     top_k=5, filtros={"tipo": "comunicacion"})
FIRMWARE = SearchQuery(consulta="Identifique el firmware anunciado por COM-PRV-0134 y las condiciones de aplicación.",
                       top_k=10, filtros={"tipo": "comunicacion"})
ANNEX = FragmentQuery(doc_id=DOCUMENT, version_documental=None, section_id=SECTION)


def configure_inspector(inspector, workspace, services, catalog_path):
    servers = {}
    for name, service in services.items():
        fixture = {"catalog": str(catalog_path), "index": str(service.root),
                   "context": context_data(service.policy.context), "at": service.policy.clock().isoformat()}
        path = workspace / f"{name}.json"
        path.write_text(json.dumps(fixture), encoding="utf-8")
        servers[name] = server_entry(sys.executable, [str(APP_ROOT / "tools/f9_observe.py"), str(path)])
    inspector.configure(servers)
    return verify_list(inspector)


def save_call(destination, query, service, report, events):
    write_report(destination / "python.json", {"entrada": query.model_dump(mode="json"),
                 "contexto": context_data(service.policy.context), "instante": service.policy.clock().isoformat(),
                 "efectos_observados": events, "resultado": report["resultado"],
                 "texto": report.get("texto")}, emit=False)
    write_report(destination / "traza.json", report["traza"], emit=False)


def compare_call(destination, inspector, tools, label, name, service, query):
    tool = SEARCH if isinstance(query, SearchQuery) else DIRECT
    with observed() as python_events:
        report = answer(service, query) if tool == SEARCH else service.obtain(query)
    save_call(destination / label, query, service, report, python_events)
    result, stderr = inspector.run(f"{label}/inspector", name, tool=tool, arguments=query.model_dump(mode="json"))
    mcp = validated(result, tool, tools)
    markers = [json.loads(line.split(MARKER, 1)[1]) for line in stderr.splitlines() if MARKER in line]
    python = report["resultado"]
    parity = {key: val for key, val in python.items() if key != "correlation_id"} == {
        key: val for key, val in mcp.items() if key != "correlation_id"}
    if tool == SEARCH:
        parity = parity and [item["text"] for item in result["content"][1:]] == [report["texto"]]
    checks = {"paridad_python_mcp": parity, "observador_mcp_activo": len(markers) == 1,
              "sin_efectos_observados": not python_events and markers == [[]]}
    write_report(destination / label / "comparacion.json", checks | {"observaciones_mcp": markers}, emit=False)
    return report, checks


def contains_payload(report):
    output = json.dumps({key: report[key] for key in ("resultado", "texto")}, ensure_ascii=False).casefold()
    return any(marker in output for marker in PAYLOAD_MARKERS)


def verify_cases(destination, inspector, tools, services, fragments, annex):
    history = services["historico"]
    with observed() as raw_events:
        raw = history.search(ATTACK)
    save_call(destination / "recuperacion", ATTACK, history, raw, raw_events)
    for branch, candidates in candidate_details(raw["traza"], fragments).items():
        write_report(destination / "recuperacion" / f"{branch}.json", {"candidatos": candidates}, emit=False)
    attack, attack_checks = compare_call(destination, inspector, tools, "ataque", "historico", history, ATTACK)
    audit, audit_checks = compare_call(destination, inspector, tools, "anexo-directo", "auditoria",
                                      services["auditoria"], ANNEX)
    firmware, firmware_checks = compare_call(destination, inspector, tools, "firmware", "historico", history, FIRMWARE)

    chunk = annex["chunk_id"]
    found, rejected = raw["resultado"], attack["resultado"]
    checks = {
        "recuperacion": {"anexo_integro_recuperado": found["estado"] == "recuperada"
                         and any(part == annex for part in found["evidencia"]),
                         "sin_efectos_observados": not raw_events},
        "ataque": attack_checks | {"anexo_descartado_en_composicion": chunk in attack["traza"].get(
            "descartados_seguridad", ()) and found["generation_id"] == rejected["generation_id"],
            "abstencion_sin_citas_ni_instrucciones": rejected["estado"] == "abstencion"
            and rejected["motivo_abstencion"] == "evidencia_insuficiente"
            and not rejected["afirmaciones"] and not rejected["evidencia"] and not contains_payload(attack)},
        "anexo_directo": audit_checks | {"lectura_integra_como_dato_no_confiable":
            audit["resultado"]["estado"] == "encontrado" and audit["resultado"]["partes"] == [annex]},
        "firmware": firmware_checks | {"version_y_condiciones_citadas": firmware["resultado"]["estado"] == "respondida"
            and all(word in firmware["texto"] for word in ("7.4", "fuera de servicio", "verificación del factor"))
            and {(cite["doc_id"], cite["section_id"]) for claim in firmware["resultado"]["afirmaciones"]
                 for cite in claim["citas"]} == {(DOCUMENT, section) for section in
                                                 ("asunto", "contenido-de-la-version", "condiciones-de-aplicacion")},
            "sin_instrucciones_del_anexo": not contains_payload(firmware)},
    }
    return checks


def run(workspace, destination, historical, fragments):
    context, audit_index, annex = prepare_audit(workspace, historical, destination)
    catalog_path = workspace / "review.sqlite3"
    before = file_digest(catalog_path)
    probes = self_check(workspace)
    with Catalog.open(catalog_path, "laboratorio", read_only=True) as catalog:
        snapshot = catalog.snapshot()
        services = {name: Retriever(root, EligibilityService(catalog, service_context, clock=historical.policy.clock),
                                    historical.encoder) for name, root, service_context in (
            ("historico", historical.root, historical.policy.context), ("auditoria", audit_index, context))}
        inspector = Inspector(workspace, destination)
        tools = configure_inspector(inspector, workspace, services, catalog_path)
        checks = verify_cases(destination, inspector, tools, services, fragments, annex)
        same_snapshot = catalog.snapshot() == snapshot
    after = file_digest(catalog_path)
    checks["entorno"] = {"catalogo_y_revision_intactos": same_snapshot and before == after and snapshot.revision == 13,
                         "solo_herramientas_de_lectura": set(tools) == {SEARCH, DIRECT},
                         "sondas_locales_bloqueadas": {row["categoria"] for row in probes} ==
                         {"procesos", "red", "balances"}}
    return {"status": "passed" if all(all(case.values()) for case in checks.values()) else "failed",
            "alcance": "ensayo técnico histórico de servidor; no es una evaluación de un cliente LLM",
            "inspector": inspector.version, "revision_gobierno": snapshot.revision, "herramientas": list(tools),
            "anexo_chunk_id": annex["chunk_id"], "pdf_sha256": annex["pdf_sha256"],
            "catalogo_sha256_antes": before, "catalogo_sha256_despues": after,
            "sondas_control_positivas": probes, "comprobaciones": checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    destination = (APP_ROOT / parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    try:
        configure_cache(offline=True)
        with TemporaryDirectory(prefix="petroandes-f9-") as directory, MonkeyPatch.context() as patch:
            workspace = Path(directory)
            with historical_lab(workspace, patch) as (historical, fragments):
                summary = run(workspace, destination, historical, fragments)
    except (AssertionError, OSError, RuntimeError, KeyError, ValueError, StopIteration) as exc:
        summary = {"status": "failed", "tipo": type(exc).__name__, "motivo": str(exc)}
    write_report(destination / "summary.json", summary)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
