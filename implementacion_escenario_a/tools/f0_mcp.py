"""Verifica listado y llamada con el MCP Inspector real, nunca un cliente simulado."""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from project_paths import INSPECTOR_DIR, CACHE_DIR
from f0_common import ROOT, write_report
from record_command import record


def result_payload(output):
    data = json.loads(output)
    return data.get("result", data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    destination = ROOT / args.output_dir
    destination.mkdir(parents=True, exist_ok=False)
    node = shutil.which("node")
    package = INSPECTOR_DIR / "node_modules/@modelcontextprotocol/inspector"
    metadata = json.loads((package / "package.json").read_text(encoding="utf-8"))
    launcher = package / "clients/launcher/build/index.js"
    state = CACHE_DIR / "inspector-state"
    state.mkdir(parents=True, exist_ok=True)
    config = state / "f0.json"
    config.write_text(json.dumps({"mcpServers": {"f0": {
        "command": sys.executable, "args": [str(ROOT / "tools/f0_mcp_server.py")],
        "env": {"PYTHONIOENCODING": "utf-8"}}}}, indent=2), encoding="utf-8")
    env = dict(os.environ, MCP_CLIENT_CONFIG_PATH=str(state / "client.json"),
               MCP_INSPECTOR_SECRET_STORE="memory")
    env.pop("MCP_CATALOG_PATH", None)
    base = [node, str(launcher), "--cli", "--config", str(config), "--server", "f0",
            "--protocol-era", "legacy", "--format", "json"]
    listed, stdout, _ = record(base + ["--method", "tools/list"],
                              destination / "list", timeout=120, env=env)
    if listed["exit_code"] != 0:
        raise RuntimeError(f"Inspector falló: consultar {destination / 'list'}")
    tools = result_payload(stdout)["tools"]
    assert [tool["name"] for tool in tools] == ["comprobar_entorno"], tools
    called, stdout, _ = record(base + ["--method", "tools/call", "--tool-name",
        "comprobar_entorno"], destination / "call", timeout=120, env=env)
    assert called["exit_code"] == 0, called
    result = result_payload(stdout)
    assert not result.get("isError", False), result
    text_blocks = [item["text"] for item in result["content"] if item["type"] == "text"]
    body = result.get("structuredContent") or json.loads("".join(text_blocks))
    assert body.get("estado") == "ok" and body.get("fase") == "F0", body
    write_report(destination / "summary.json", {"status": "passed",
        "inspector_version": metadata["version"], "node": node,
        "sdk_protocol_era": "legacy", "transport": "stdio",
        "listed_tools": [tool["name"] for tool in tools], "call_result": body,
        "list_seconds": listed["elapsed_seconds"], "call_seconds": called["elapsed_seconds"],
        "scope": "F0 servidor mínimo; no acredita las dos herramientas finales de F7"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
