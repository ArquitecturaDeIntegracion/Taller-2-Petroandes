import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from petroandes import paths


def test_relative_config_ignores_working_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("PETROANDES_TEST_DIR", "datos/modelos")
    monkeypatch.chdir(tmp_path.parent)
    assert paths.configured("PETROANDES_TEST_DIR", "unused", tmp_path) == (
        tmp_path / "datos/modelos").resolve()


@pytest.mark.parametrize("value", ["../escape", "a/../../escape", "C:\\Users\\otro",
                                  "/tmp/external", "\\\\host\\share\\weights"])
def test_references_reject_absolute_or_escape(value, tmp_path):
    with pytest.raises(ValueError):
        paths.relative_path(value, tmp_path)


def test_legacy_relative_windows_reference(tmp_path):
    assert paths.relative_path("model\\tokenizer.json", tmp_path) == (
        tmp_path / "model/tokenizer.json").resolve()


def test_legacy_model_report_does_not_consume_old_machine_path():
    report = {"revision": "a" * 40, "snapshot": "C:\\Users\\otra-maquina\\pesos"}
    assert paths.resolve_model_report(report, "e5") == paths.MODELS_DIR / ("e5-" + "a" * 40)


def test_model_reference_and_redacted_evidence_roundtrip():
    location = paths.MODELS_DIR / "example/config.json"
    ref = paths.model_reference(location)
    assert ref == {"base": "models", "path": "example/config.json"}
    assert paths.resolve_model_report({"snapshot_ref": ref}, "e5") == location
    value = paths.portable({"command": [sys.executable, str(paths.APP_ROOT / "tools/f0.py")]})
    assert value["command"][0] == "python"
    assert str(paths.APP_ROOT) not in json.dumps(value)
    assert "${APP_ROOT}" in paths.portable(repr(str(paths.APP_ROOT)))


def test_reader_after_relocation_with_spaces_and_different_cwd(tmp_path):
    project = tmp_path / "clon con á"
    app = project / "app"
    (app / "tools").mkdir(parents=True)
    (app / "knowledge").mkdir()
    shutil.copytree(paths.APP_ROOT / "petroandes", app / "petroandes",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for filename in ("project_paths.py", "read_source.py"):
        shutil.copyfile(paths.APP_ROOT / "tools" / filename, app / "tools" / filename)
    source = project / "ejemplo.md"
    source.write_text("# Ejemplo\nContenido portable\n", encoding="utf-8")
    registry = {"sources": [{"id": "ejemplo", "path": source.name,
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}
    (app / "knowledge/sources.json").write_text(json.dumps(registry), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PETROANDES_")}
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([sys.executable, "-B", str(app / "tools/read_source.py"),
                             "ejemplo"], cwd=tmp_path, env=env,
                            capture_output=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0, result.stderr
    assert "Contenido portable" in result.stdout


def test_windows_dependency_skipped_for_linux():
    from packaging.markers import default_environment
    from packaging.requirements import Requirement
    entries = (paths.APP_ROOT / "requirements-portable.lock").read_text().splitlines()
    requirement = Requirement(next(line for line in entries if line.startswith("pywin32")))
    environment = {**default_environment(), "sys_platform": "linux"}
    assert not requirement.marker.evaluate(environment)
