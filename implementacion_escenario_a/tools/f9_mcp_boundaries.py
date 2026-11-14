"""Integración MCP real: gobierno por objeto, huella y contexto histórico aislado."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import MonkeyPatch

from f0_common import configure_cache, write_report
from f7_inspector import DIRECT, SEARCH, historical_lab, validated
from f7_inspector_client import Inspector
from f9_attack import configure_inspector
from f9_sources import DOCUMENT, prepare_audit
from petroandes.catalog.api import Catalog
from petroandes.governance.eligibility import EligibilityService
from petroandes.index.common import context_data, file_digest
from petroandes.paths import APP_ROOT
from petroandes.retrieve import Retriever

PENDING = {"doc_id": "MAN-OPE-004", "version_documental": "2", "section_id": "3"}
EXCLUDED = {"doc_id": "PRO-MED-007", "version_documental": "1", "section_id": "3"}
DISTINCT = {"doc_id": "RES-CREG-0043-2024", "version_documental": None, "section_id": "articulo-2"}
EXTRAS = {"perfil": "laboratorio", "grupos": ["LAB_REVISION"], "uso": "inspeccion_no_confiable"}


def check_invalid(result):
    """Un error de dominio o una salida vacía no acredita rechazo del esquema MCP."""
    assert result.get("isError") is True, "Falta error de herramienta MCP"
    assert not result.get("structuredContent"), "El rechazo revela contenido estructurado"
    assert [item.get("text") for item in result.get("content", [])] == ["parametros_invalidos"]


def check_denied(body):
    assert body["estado"] == "denegado", "Error/abstención no equivalen a denegación"
    assert body["error"] == "evidencia_no_autorizada"
    assert body["partes"] == body["citas"] == [], "La denegación filtra evidencia"
    assert body["revision_gobierno"] == 13


def check_found(body, query):
    assert body["estado"] == "encontrado" and body["revision_gobierno"] == 13
    assert body["generation_id"] and body["partes"] and body["citas"]
    assert all(part["doc_id"] == query["doc_id"]
               and part["version_documental"] == query["version_documental"]
               and part["section_id"] == query["section_id"]
               and ("pdf_sha256" not in query or part["pdf_sha256"] == query["pdf_sha256"])
               and part["contenido_no_confiable"] for part in body["partes"])


def call(inspector, tools, label, server, tool, query, *, invalid=False):
    result, _ = inspector.run(label, server, tool=tool, arguments=query,
                              expected_exit=5 if invalid else 0)
    if invalid:
        check_invalid(result)
        return None
    return validated(result, tool, tools)


def verify_boundaries(inspector, tools, services, sha256, destination):
    checks = {}
    reference = {"doc_id": DOCUMENT, "version_documental": None, "section_id": "asunto", "pdf_sha256": sha256}
    other_hash = ("0" if sha256[0] != "0" else "1") + sha256[1:]
    for server in services:
        for tool, query in ((SEARCH, {"consulta": "COM-PRV-0134", "top_k": 1}), (DIRECT, reference)):
            label = f"{server}/extras-{tool}"
            call(inspector, tools, label, server, tool, query | EXTRAS, invalid=True)
            checks[label] = True
            write_report(destination / label / "assessment.json", {
                "caso": label, "frontera": "MCP real/esquema", "entrada": query | EXTRAS,
                "esperado": "parametros_invalidos", "observado": "parametros_invalidos",
                "comprobado": True}, emit=False)
        for label, query, expected in (
            ("hash-exacto", reference, "encontrado"),
            ("hash-ajeno", reference | {"pdf_sha256": other_hash}, "denegado"),
            ("excluido", EXCLUDED, "denegado"), ("pendiente", PENDING, "denegado"),
            ("objeto-otro-contexto", DISTINCT, "encontrado" if server == "historico" else "denegado"),
        ):
            key = f"{server}/{label}"
            body = call(inspector, tools, key, server, DIRECT, query)
            check_found(body, query) if expected == "encontrado" else check_denied(body)
            checks[key] = True
            write_report(destination / key / "assessment.json", {
                "caso": key, "frontera": "MCP real/gobierno documental", "entrada": query,
                "esperado": expected, "observado": body["estado"], "revision_gobierno": body["revision_gobierno"],
                "generation_id": body["generation_id"], "comprobado": True}, emit=False)
    return checks


def exercise(workspace, destination, historical):
    catalog_path = workspace / "review.sqlite3"
    original = APP_ROOT / "evidence/lab/20261103/registration/laboratorio-after.sqlite3"
    source_before, copy_before = file_digest(original), file_digest(catalog_path)
    assert source_before == copy_before, "La copia histórica inicial difiere del snapshot archivado"
    context, audit_root, annex = prepare_audit(workspace, historical, destination)
    with Catalog.open(catalog_path, "laboratorio", read_only=True) as catalog:
        snapshot = catalog.snapshot()
        services = {name: Retriever(root, EligibilityService(catalog, ctx, clock=historical.policy.clock), historical.encoder)
                    for name, root, ctx in (("historico", historical.root, historical.policy.context),
                                            ("auditoria", audit_root, context))}
        assert snapshot.revision == 13
        assert services["historico"].root != services["auditoria"].root
        assert services["historico"].policy.context.uso == "evidencia_historica"
        assert services["auditoria"].policy.context.uso == "inspeccion_no_confiable"
        inspector = Inspector(workspace, destination)
        tools = configure_inspector(inspector, workspace, services, catalog_path)
        listed, _ = inspector.run("list-auditoria", "auditoria")
        expected, _ = inspector.run("list-historico-repetido", "historico")
        assert listed == expected, "Los contextos exponen catálogos MCP diferentes"
        assert set(tools) == {SEARCH, DIRECT}
        checks = verify_boundaries(inspector, tools, services, annex["pdf_sha256"], destination)
        checks["contextos_aislados_snapshot13"] = True
        checks["catalogo_snapshot_intacto"] = catalog.snapshot() == snapshot
        write_report(destination / "contextos.json", {
            "revision_gobierno": snapshot.revision, "instante": historical.policy.clock().isoformat(),
            "contextos": {name: {"contexto": context_data(service.policy.context), "index": str(service.root)}
                          for name, service in services.items()}}, emit=False)
    source_after, copy_after = file_digest(original), file_digest(catalog_path)
    checks["huellas_catalogos_intactas"] = source_before == source_after == copy_before == copy_after
    return {"status": "passed" if all(checks.values()) else "failed", "alcance": "integración MCP real; snapshot13 aislado",
            "llm": "no_evaluado", "inspector": inspector.version, "revision_gobierno": 13,
            "herramientas": list(tools), "comprobaciones": checks,
            "catalogo_sha256_antes": copy_before, "catalogo_sha256_despues": copy_after,
            "original_sha256_antes": source_before, "original_sha256_despues": source_after}


def run(destination: Path) -> dict:
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    try:
        configure_cache(offline=True)
        with TemporaryDirectory(prefix="petroandes-f9-mcp-") as directory, MonkeyPatch.context() as patch:
            workspace = Path(directory)
            with historical_lab(workspace, patch) as (historical, _):
                summary = exercise(workspace, destination, historical)
    except Exception as exc:
        summary = {"status": "failed", "tipo": type(exc).__name__, "motivo": str(exc),
                   "alcance": "integración MCP real; fallo no equivale a ataque bloqueado", "llm": "no_evaluado"}
    write_report(destination / "summary.json", summary, emit=False)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    summary = run(APP_ROOT / parser.parse_args().output_dir)
    print(json.dumps({"status": summary["status"], "alcance": summary["alcance"]}, ensure_ascii=False))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
