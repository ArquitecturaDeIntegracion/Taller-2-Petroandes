"""Comprueba una copia aislada del taller usando el intérprete actual, sin copiar .venv."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from project_paths import APP_ROOT, PROJECT_ROOT, relative_path
from f0_common import write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    artifacts = APP_ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    registry = json.loads((APP_ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    env = {k: v for k, v in os.environ.items() if not k.startswith("PETROANDES_")}
    env["PYTHONIOENCODING"] = "utf-8"
    results = []
    # Todo el temporal queda bajo artifacts; no se toca la instalación original.
    with TemporaryDirectory(prefix="clon portable á ", dir=artifacts) as temporary:
        project = Path(temporary) / "taller copiado"
        app = project / APP_ROOT.name
        outside = Path(temporary) / "cwd externo"
        outside.mkdir()
        excluded = shutil.ignore_patterns(".venv", "venv", ".cache", "__pycache__",
            ".pytest_cache", ".git", "artifacts", "*.egg-info", "build", "dist", ".env", ".env.*")
        shutil.copytree(APP_ROOT, app, ignore=excluded)
        # Los informes recientes no son fuentes ni evidencia histórica versionada.
        copied_reports = app / "reports/portable"
        if copied_reports.exists():
            if not copied_reports.resolve().is_relative_to(app.resolve()):
                raise ValueError("Destino de limpieza fuera de la copia")
            shutil.rmtree(copied_reports)
        for source in registry["sources"]:
            destination = relative_path(source["path"], project)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(relative_path(source["path"], PROJECT_ROOT), destination)
        shutil.copytree(PROJECT_ROOT / "corpus", project / "corpus", dirs_exist_ok=True)
        shutil.copy2(PROJECT_ROOT / "ARTI4212_Caso_PetroAndes.pdf", project)
        env["PYTHONPATH"] = str(app)
        commands = [
            ("preflight", [str(app / "tools/preflight.py")]),
            ("validate_agent", [str(app / "tools/validate_agent.py")]),
            ("pytest", ["-m", "pytest", "-q", "-p", "no:cacheprovider", "-c",
                        str(app / "pyproject.toml"), str(app / "tests"), "--basetemp",
                        str(Path(temporary) / "tests")]),
        ]
        for name, command in commands:
            result = subprocess.run([sys.executable, "-B", *command], cwd=outside,
                env=env, capture_output=True, encoding="utf-8", timeout=120)
            results.append({"check": name, "exit_code": result.returncode,
                "stdout_tail": result.stdout.splitlines()[-45 if result.returncode else -2:],
                "stderr_tail": result.stderr.splitlines()[-5:]})
        complete = all(item["exit_code"] == 0 for item in results)
        write_report(APP_ROOT / args.output, {"status": "passed" if complete else "failed",
            "clone": "Copia temporal con espacios y á, eliminada al terminar",
            "working_directory": "Externo a la aplicación copiada",
            "interpreter": "Reutilizado del entorno actual; no acredita instalación limpia",
            "models_and_venv_copied": False, "checks": results})
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
