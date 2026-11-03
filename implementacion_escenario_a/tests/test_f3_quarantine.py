"""Fallo real de contraste en una copia: el documento no produce fragmentos."""
import json
import os
import shutil
import subprocess
import sys

from petroandes.paths import APP_ROOT, PROJECT_ROOT


def test_bad_document_is_reported_and_omitted_without_authorizing_corpus(tmp_path):
    project = tmp_path / "taller-copia"
    shutil.copytree(PROJECT_ROOT / "corpus", project / "corpus")
    md = project / "corpus/md/04_actas/ACTA-CTO-2025-07.md"
    original = md.read_text(encoding="utf-8")
    md.write_text(original.replace("no son exigibles", "son exigibles"), encoding="utf-8")
    artifacts = tmp_path / "artifacts"
    target = artifacts / "catalog/baseline/catalog.sqlite3"
    target.parent.mkdir(parents=True)
    shutil.copyfile(APP_ROOT / "evidence/f2/initial-20261101/baseline/catalog.sqlite3", target)
    output = tmp_path / "ingesta"
    env = {**os.environ, "PETROANDES_PROJECT_ROOT": str(project),
           "PETROANDES_ARTIFACTS_DIR": str(artifacts), "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run([sys.executable, "-m", "petroandes.extract", "--output-dir", str(output)],
        cwd=APP_ROOT, env=env, capture_output=True, encoding="utf-8", timeout=120)
    assert result.returncode == 1, result.stderr
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["preparados"] == 18 and manifest["rechazados"] == 1
    assert manifest["publication_state"] == "staging_no_autorizado"
    records = [json.loads(line) for name in manifest["fragment_files"]
               for line in (output / name).read_text(encoding="utf-8").splitlines()]
    assert not any(item["fragment"]["doc_id"] == "ACTA-CTO-2025-07" for item in records)
    assert all(item["metadata"]["gobierno"]["decision_id"] is None for item in records)
    affected = [json.loads((output / name).read_text(encoding="utf-8"))
                for name in manifest["document_reports"]]
    assert any(item["status"] == "requiere_revision" and "Diferencia" in item["motivo"] for item in affected)
