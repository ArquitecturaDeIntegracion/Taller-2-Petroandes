"""Generación SQLite real, idempotencia y rechazo de corrupción sin activar índices."""
import copy
import json
import sqlite3
from contextlib import closing

import pytest
from petroandes.extract import staging
from petroandes.extract.models import ExtractionReview


def fixture_records():
    manifest = {"perfil": "baseline", "generation_id": "fixture-sintetico", "publication_state": "staging_no_autorizado"}
    record = {"fragment": {"chunk_id": "sintetico", "parent_id": "padre"},
              "metadata": {"ingested_at": "primera-corrida", "gobierno": {"estado": "pendiente"}},
              "embedding_input": "passage: fixture sintético"}
    parent = {"parent_id": "padre", "text": "texto sintético", "lines": [(1, 2)]}
    return manifest, [record], [parent]


def test_repeat_reuses_generation_without_additional_identities(tmp_path, monkeypatch):
    monkeypatch.setattr(staging, "ARTIFACTS_DIR", tmp_path)
    manifest, records, parents = fixture_records()
    path, reused = staging.store_generation(manifest, records, parents)
    assert not reused
    second = copy.deepcopy(records)
    second[0]["metadata"]["ingested_at"] = "segunda-corrida"
    assert staging.store_generation(manifest, second, parents) == (path, True)
    with closing(sqlite3.connect(path / "fragments.sqlite3")) as db:
        assert db.execute("SELECT count(*) FROM fragments").fetchone()[0] == 1
        assert json.loads(db.execute("SELECT payload FROM manifest").fetchone()[0])["publication_state"] == "staging_no_autorizado"


@pytest.mark.parametrize("sql", ["UPDATE fragments SET payload='{}'", "UPDATE parents SET payload='{}'"])
def test_modified_payload_is_not_silently_reused(tmp_path, monkeypatch, sql):
    monkeypatch.setattr(staging, "ARTIFACTS_DIR", tmp_path)
    manifest, records, parents = fixture_records()
    path, _ = staging.store_generation(manifest, records, parents)
    with closing(sqlite3.connect(path / "fragments.sqlite3")) as db, db:
        db.execute(sql)
    with pytest.raises(ExtractionReview):
        staging.store_generation(manifest, records, parents)
