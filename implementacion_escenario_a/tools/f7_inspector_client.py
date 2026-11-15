"""Lanzador local del Inspector fijado, con configuración efímera."""
import json
import os
import shutil

from project_paths import APP_ROOT, INSPECTOR_DIR, portable
from record_command import record


class Inspector:
    def __init__(self, workspace, destination):
        self.destination = destination
        self.node = shutil.which("node")
        if not self.node:
            raise RuntimeError("Node no está en PATH")
        package = INSPECTOR_DIR / "node_modules/@modelcontextprotocol/inspector"
        self.version = json.loads((package / "package.json").read_text(encoding="utf-8"))["version"]
        self.launcher = package / "clients/launcher/build/index.js"
        self.config = workspace / "servers.json"
        self.env = {**os.environ, "MCP_CLIENT_CONFIG_PATH": str(workspace / "client.json"),
                    "MCP_INSPECTOR_SECRET_STORE": "memory"}
        self.env.pop("MCP_CATALOG_PATH", None)

    def configure(self, servers):
        config = {"mcpServers": servers}
        self.config.write_text(json.dumps(config), encoding="utf-8")
        (self.destination / "config-portable.json").write_text(
            json.dumps(portable(config), indent=2) + "\n", encoding="utf-8")

    def run(self, label, server, *, tool=None, arguments=None, expected_exit=0):
        command = [self.node, str(self.launcher), "--cli", "--config", str(self.config), "--server", server,
                   "--protocol-era", "legacy", "--format", "json"]
        if tool:
            command += ["--method", "tools/call", "--tool-name", tool,
                        "--tool-args-json", json.dumps(arguments, ensure_ascii=False)]
        else:
            command += ["--method", "tools/list"]
        receipt, stdout, stderr = record(command, self.destination / label, timeout=120, env=self.env)
        if receipt["exit_code"] != expected_exit:
            raise RuntimeError(f"Inspector devolvió código {receipt['exit_code']} en {label}; se esperaba {expected_exit}")
        return json.loads(stdout)["result"], stderr


def server_entry(command, args, **extra_env):
    overrides = ("PETROANDES_PROJECT_ROOT", "PETROANDES_CACHE_DIR", "PETROANDES_MODELS_DIR", "PETROANDES_AUDIT_DIR")
    environment = {key: os.environ[key] for key in overrides if key in os.environ}
    environment.update(extra_env)
    return {"command": command, "args": args, "cwd": str(APP_ROOT),
            "env": {**environment, "PYTHONIOENCODING": "utf-8"}}
