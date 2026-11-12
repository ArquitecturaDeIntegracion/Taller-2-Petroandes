"""Verificación F7 con Inspector real y un laboratorio histórico desechable."""
import argparse
import json
import re
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from jsonschema import Draft202012Validator
from pytest import MonkeyPatch

from project_paths import APP_ROOT
from f0_common import configure_cache, write_report
from f7_inspector_client import Inspector, server_entry
from record_command import record
from petroandes.compose import answer
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.index.publication import Publisher
from petroandes.mcp_tools import CONTRACTS, CONTRACT_VERSION

sys.path.insert(0, str(APP_ROOT / "tests"))
from historical_lab import historical_lab

SEARCH = "buscar_documentos"
DIRECT = "obtener_fragmento"
QUESTION = {"consulta": "Presión de descarga documentada de P-101.", "top_k": 3,
            "filtros": {"tipo": "ficha", "activo": "P-101"}}
SECTION = {"doc_id": "RES-CREG-0043-2024", "version_documental": None, "section_id": "articulo-2"}
PENDING = {"doc_id": "MAN-OPE-004", "version_documental": "2", "section_id": "3"}


def fixture_config(workspace, service):
    fixture = {"catalog": str(workspace / "review.sqlite3"), "index": str(service.root),
               "context": service.policy.context.model_dump(mode="json"),
               "at": service.policy.clock().isoformat()}
    entries = {}
    for name, values in (("historico", fixture), ("sin_indice", fixture | {"index": str(workspace / "ausente")})):
        path = workspace / f"{name}.json"
        path.write_text(json.dumps(values), encoding="utf-8")
        entries[name] = server_entry(sys.executable, [str(APP_ROOT / "tests/f7_stdio_fixture.py"), str(path)])
    artifacts = workspace / "despliegue"
    destination = artifacts / "catalog/laboratorio/catalog.sqlite3"
    destination.parent.mkdir(parents=True)
    copyfile(fixture["catalog"], destination)
    for name, root in (("habitual", artifacts), ("sin_catalogo", workspace / "sin-catalogo")):
        entries[name] = server_entry(sys.executable, ["-m", "petroandes.mcp_server", "--profile", "laboratorio"],
                                     PETROANDES_ARTIFACTS_DIR=str(root))
    return entries


def verify_list(inspector):
    listed, _ = inspector.run("list", "historico")
    tools = {tool["name"]: tool for tool in listed["tools"]}
    assert len(listed["tools"]) == 2 and tools.keys() == CONTRACTS.keys()
    for name, (query, response, _) in CONTRACTS.items():
        tool = tools[name]
        assert tool["annotations"]["readOnlyHint"]
        assert tool["inputSchema"] == query.model_json_schema()
        assert tool["outputSchema"] == response.model_json_schema(mode="serialization")
        Draft202012Validator.check_schema(tool["inputSchema"])
        Draft202012Validator.check_schema(tool["outputSchema"])
    return tools


def validated(result, tool, tools):
    assert not result.get("isError", False), result
    body = result["structuredContent"]
    Draft202012Validator(tools[tool]["outputSchema"]).validate(body)
    CONTRACTS[tool][1].model_validate(body)
    assert json.loads(result["content"][0]["text"]) == body
    return body


def equivalent(left, right):
    assert left["correlation_id"] != right["correlation_id"]
    assert {key: value for key, value in left.items() if key != "correlation_id"} == {
        key: value for key, value in right.items() if key != "correlation_id"}


def verify_positive(inspector, service, tools):
    direct_search = answer(service, SearchQuery.model_validate(QUESTION))
    first, stderr = inspector.run("search-ok", "historico", tool=SEARCH, arguments=QUESTION)
    search = validated(first, SEARCH, tools)
    assert search["estado"] == "respondida" and search["revision_gobierno"] == 13
    assert "1.180 psi" in search["afirmaciones"][0]["texto"] and "1.240 psi" in search["afirmaciones"][0]["texto"]
    assert all(part["doc_id"] == "FIC-ACT-P101" for part in search["evidencia"])
    assert first["content"][1]["text"] == direct_search["texto"]
    equivalent(search, direct_search["resultado"])
    direct, _ = inspector.run("direct-ok", "historico", tool=DIRECT, arguments=SECTION)
    obtained = validated(direct, DIRECT, tools)
    assert obtained["estado"] == "encontrado" and obtained["citas"][0]["version_documental"] is None
    assert obtained["partes"][0]["contenido_no_confiable"] and "0,3 %" in obtained["partes"][0]["texto"]
    equivalent(obtained, service.obtain(FragmentQuery.model_validate(SECTION))["resultado"])
    repeat, later_stderr = inspector.run("reconnect", "historico", tool=SEARCH, arguments=QUESTION)
    reopened = validated(repeat, SEARCH, tools)
    equivalent(search, reopened)
    first_pid = re.search(r"F7 fixture stdout Python pid=(\d+)", stderr)
    second_pid = re.search(r"F7 fixture stdout Python pid=(\d+)", later_stderr)
    assert first_pid and second_pid and first_pid[1] != second_pid[1]
    with Publisher(service.root, service.policy, service.encoder) as publisher:
        manifest, _ = publisher.active()
        assert manifest.generation_id == search["generation_id"] and len(manifest.fragmentos) == 58
    return search["generation_id"]


def verify_negative(inspector, service, tools):
    abstention, _ = inspector.run("search-abstention", "habitual", tool=SEARCH, arguments=QUESTION)
    response = validated(abstention, SEARCH, tools)
    assert response["estado"] == "abstencion" and response["motivo_abstencion"] == "sin_evidencia_autorizada"
    assert response["evidencia"] == response["afirmaciones"] == [] and response["revision_gobierno"] == 13

    denied, _ = inspector.run("direct-denied", "historico", tool=DIRECT, arguments=PENDING)
    response = validated(denied, DIRECT, tools)
    assert response["estado"] == "denegado" and response["error"] == "evidencia_no_autorizada"
    assert response["partes"] == response["citas"] == []
    equivalent(response, service.obtain(FragmentQuery.model_validate(PENDING))["resultado"])

    for name, server, code in (("index-error", "sin_indice", "indice_no_listo"),
                               ("service-error", "sin_catalogo", "servicio_no_disponible")):
        result, _ = inspector.run(name, server, tool=SEARCH, arguments=QUESTION)
        response = validated(result, SEARCH, tools)
        assert response["estado"] == "error" and response["error"] == code and not response["evidencia"]

    for label, tool, arguments in (
        ("search-invalid", SEARCH, {"consulta": "diagnostico", "top_k": 0}),
        ("direct-invalid", DIRECT, {"doc_id": SECTION["doc_id"], "section_id": SECTION["section_id"]}),
        ("privilege-invalid", SEARCH, QUESTION | {"perfil": "laboratorio", "grupos": ["LAB_REVISION"]}),
    ):
        invalid, _ = inspector.run(label, "historico", tool=tool, arguments=arguments, expected_exit=5)
        assert invalid.get("isError") and not invalid.get("structuredContent")
        assert [item["text"] for item in invalid["content"]] == ["parametros_invalidos"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    destination = (APP_ROOT / parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    configure_cache(offline=True)
    with TemporaryDirectory(prefix="petroandes-f7-") as directory, MonkeyPatch.context() as patch:
        workspace = Path(directory)
        with historical_lab(workspace, patch) as (service, _):
            inspector = Inspector(workspace, destination)
            servers = fixture_config(workspace, service)
            inspector.configure(servers)
            tools = verify_list(inspector)
            generation = verify_positive(inspector, service, tools)
            verify_negative(inspector, service, tools)
            wire, stdout, stderr = record(
                [sys.executable, str(APP_ROOT / "tools/f7_wire.py"), sys.executable, *servers["historico"]["args"]],
                destination / "wire", timeout=120)
            assert wire["exit_code"] == 0
            init = json.loads(stdout.splitlines()[0])["result"]
            assert init["serverInfo"]["version"] == CONTRACT_VERSION
            for marker in ("F7 fixture stdout Python", "F7 fixture stdout nativo"):
                assert marker in stderr and marker not in stdout
            node_version = subprocess.check_output([inspector.node, "--version"], text=True).strip()
            write_report(destination / "summary.json", {"status": "passed", "inspector": inspector.version,
                "sdk_mcp": version("mcp"), "node": node_version, "transport": "stdio",
                "protocol_era_inspector": "legacy", "protocol_version_wire": init["protocolVersion"],
                "server_info": init["serverInfo"], "tools": list(tools), "generation_id": generation,
                "revision_gobierno": 13, "reopened_qdrant_points": 58, "python_parity": True,
                "inspector_tool_error_exit_code": 5,
                "clean_stdout": True, "inspector_reconnected": True,
                "scope": "ensayo histórico temporal y contexto habitual sobre una copia de catálogo"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
