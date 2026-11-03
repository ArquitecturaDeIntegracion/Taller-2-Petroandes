"""CLI real: carga PDF, exportación y reapertura, sin reemplazar datos existentes."""
import json
import os
import subprocess
import sys

from petroandes.paths import APP_ROOT


def test_cli_initializes_and_reopens_but_never_overwrites(tmp_path):
    evidence = tmp_path / "evidence"
    env = {**os.environ, "PETROANDES_ARTIFACTS_DIR": str(tmp_path / "data"),
           "PYTHONIOENCODING": "utf-8"}
    base = [sys.executable, "-m", "petroandes.catalog"]
    command = base + ["init", "--evidence-dir", str(evidence)]
    result = subprocess.run(command, cwd=APP_ROOT, env=env, capture_output=True,
                            encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["indices_construidos"] is False
    assert report["index_ref"] == {"base": "artifacts", "path": "indexes/baseline"}
    assert (evidence / "catalog.sqlite3").is_file()
    assert len(list((evidence / "observations").glob("*.json"))) == 19
    reopened = subprocess.run(base + ["status"], cwd=APP_ROOT, env=env, capture_output=True,
                              encoding="utf-8", timeout=30)
    assert reopened.returncode == 0, reopened.stderr
    assert json.loads(reopened.stdout)["clasificacion"] == {
        "pendiente": 15, "excluido": 4, "certificado": 0}
    repeated = subprocess.run(command, cwd=APP_ROOT, env=env, capture_output=True,
                              encoding="utf-8", timeout=30)
    assert repeated.returncode == 2
    assert "no se sobrescribe" in repeated.stderr
