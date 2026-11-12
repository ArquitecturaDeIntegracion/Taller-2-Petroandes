"""Abre un Inspector con el servicio habitual y el ensayo histórico de F7."""
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import MonkeyPatch

from f0_common import configure_cache
from f7_inspector import fixture_config, historical_lab
from f7_inspector_client import Inspector
from project_paths import APP_ROOT


def main():
    configure_cache(offline=True)
    with TemporaryDirectory(prefix="petroandes-web-f7-") as directory, MonkeyPatch.context() as patch:
        workspace = Path(directory)
        with historical_lab(workspace, patch) as (service, _):
            server = fixture_config(workspace, service)["historico"]
        server.update(type="stdio", protocolEra="legacy")
        inspector = Inspector(workspace, workspace)
        catalog = APP_ROOT / "config/inspector-web.json"
        config = json.loads(catalog.read_text(encoding="utf-8"))
        config["mcpServers"]["petroandes-historico-f7"] = server
        inspector.config.write_text(json.dumps(config), encoding="utf-8")
        return subprocess.run(
            [inspector.node, str(inspector.launcher), "--web", "--config", str(inspector.config)],
            env=inspector.env,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
