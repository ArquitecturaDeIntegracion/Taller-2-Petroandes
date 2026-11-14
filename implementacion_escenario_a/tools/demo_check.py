"""Verifica la conexión única real por stdio en una sesión MCP persistente."""
import argparse
import asyncio
import json
import sys
from datetime import timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from petroandes.contracts.responses import FragmentResponse, SearchResponse
from petroandes.extract.output import write_json, write_jsonl
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT


def verify(case, result):
    if "error_protocolo" in case:
        assert result.isError and case["error_protocolo"] in result.content[0].text
        return {"error_protocolo": case["error_protocolo"]}
    assert not result.isError, case["id"]
    body = result.structuredContent
    model = SearchResponse if case["herramienta"] == "buscar_documentos" else FragmentResponse
    model.model_validate(body)
    assert body["estado"] == case["estado"] and body["revision_gobierno"] == 15, case["id"]
    for field in ("error", "motivo_abstencion"):
        if field in case:
            assert body[field] == case[field], case["id"]
    text = json.dumps(body, ensure_ascii=False)
    assert all(literal in text for literal in case.get("literales", ())), case["id"]
    if body["estado"] == "denegado":
        assert not body["partes"] and not body["citas"]
    if body["estado"] == "abstencion":
        assert not body["afirmaciones"] and not body["evidencia"]
    return body


async def check(destination):
    cases = json.loads((APP_ROOT / "config/demo-pruebas.json").read_text(encoding="utf-8"))["casos"]
    snapshot = APP_ROOT / "evidence/revision/20261108-confirmada/registro/laboratorio-after.sqlite3"
    before = file_digest(snapshot)
    parameters = StdioServerParameters(command=sys.executable, args=["-m", "petroandes.demo"], cwd=str(APP_ROOT))
    rows = []
    with (destination / "servidor.log").open("w", encoding="utf-8") as diagnostics:
        async with stdio_client(parameters, errlog=diagnostics) as (reader, writer):
            async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=180)) as session:
                await session.initialize()
                listed = await session.list_tools()
                tools = [tool.name for tool in listed.tools]
                assert set(tools) == {"buscar_documentos", "obtener_fragmento"}
                for case in cases:
                    result = await session.call_tool(case["herramienta"], case["argumentos"])
                    body = verify(case, result)
                    rows.append({"id": case["id"], "herramienta": case["herramienta"],
                                 "argumentos": case["argumentos"], "resultado": body, "status": "passed"})
    assert file_digest(snapshot) == before
    write_jsonl(destination, "llamadas", rows)
    return {"status": "passed", "servidor": "petroandes", "transporte": "stdio", "herramientas": tools,
            "revision": 15, "comprobaciones_tecnicas": len(rows), "snapshot_sha256": before,
            "snapshot_identico": True, "evaluacion_formal_ejecutada": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    destination = parser.parse_args().output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    summary = asyncio.run(check(destination))
    write_json(destination / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
