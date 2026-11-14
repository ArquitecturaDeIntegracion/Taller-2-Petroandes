"""Abre el Inspector web con la conexión académica única petroandes."""
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from f0_common import configure_cache
from f7_inspector_client import Inspector
from project_paths import APP_ROOT


def main():
    configure_cache(offline=True)
    with TemporaryDirectory(prefix="petroandes-web-demo-") as directory:
        workspace = Path(directory)
        inspector = Inspector(workspace, workspace)
        catalog = APP_ROOT / "config/inspector-web.json"
        config = json.loads(catalog.read_text(encoding="utf-8"))
        inspector.config.write_text(json.dumps(config), encoding="utf-8")
        return subprocess.run(
            [inspector.node, str(inspector.launcher), "--web", "--config", str(inspector.config)],
            env=inspector.env,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
