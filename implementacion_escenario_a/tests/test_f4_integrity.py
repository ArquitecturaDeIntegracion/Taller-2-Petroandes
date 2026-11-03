"""Fallos de integridad reales: archivos, payloads, perfil y barrera de gobierno."""
import json
import sqlite3

import pytest
from qdrant_client import models

from petroandes.embeddings.encoder import BundleMismatch, E5Encoder
from petroandes.index.common import IndexUnavailable
from petroandes.index.publication import Publisher, governance_fence, select
from petroandes.index.stage import Stage
from f2_helpers import catalog, policy
from f4_helpers import stage_fixture


@pytest.fixture(scope="module")
def encoder():
    return E5Encoder()


def test_bundle_artifact_hash_is_checked(tmp_path, monkeypatch):
    from petroandes.embeddings import encoder as module
    from petroandes.paths import APP_ROOT

    expected = json.loads((APP_ROOT / "config/e5-artifacts.json").read_text())
    expected["sha256"]["model.safetensors"] = "0" * 64
    (tmp_path / "config").mkdir()
    (tmp_path / "config/e5-artifacts.json").write_text(json.dumps(expected))
    monkeypatch.setattr(module, "APP_ROOT", tmp_path)
    with pytest.raises(BundleMismatch, match="model.safetensors"):
        E5Encoder()


@pytest.mark.parametrize("damage", ["vector", "payload", "catalog", "lexical", "manifest", "missing"])
def test_active_rejects_modified_projections(tmp_path, encoder, damage):
    with catalog(tmp_path) as store:
        stage = stage_fixture(store, encoder)
        root = tmp_path / "index"
        with Publisher(root, policy(store), encoder) as publisher:
            report = publisher.publish(stage)
            manifest, receipt = publisher.active()
            folder = root / "generations" / report["generation_id"]
            if damage == "payload":
                publisher.owner.client.set_payload(receipt["collection"], {"governance_revision": 999},
                    points=[manifest.fragmentos[0]], wait=True)
            elif damage == "vector":
                publisher.owner.client.update_vectors(receipt["collection"], [models.PointVectors(
                    id=manifest.fragmentos[0], vector=[1.0] + [0.0] * 383)], wait=True)
            elif damage == "missing":
                (folder / "lexical.sqlite3").unlink()
            else:
                name = "manifest.json" if damage == "manifest" else f"{damage}.sqlite3"
                with (folder / name).open("ab") as output:
                    output.write(b"alteracion")
            with pytest.raises((IndexUnavailable, OSError, sqlite3.Error)):
                publisher.active()


def test_profile_mismatch_duplicate_fragment_and_missing_parent(tmp_path, encoder):
    with catalog(tmp_path) as store:
        stage = stage_fixture(store, encoder)
        eligibility = policy(store).eligible()
        wrong = Stage(stage.manifest | {"perfil": "baseline"}, stage.records, stage.parents)
        duplicate = Stage(stage.manifest, stage.records + stage.records[:1], stage.parents)
        missing = Stage(stage.manifest, stage.records, ())
        for candidate in (wrong, duplicate, missing):
            with pytest.raises(IndexUnavailable):
                select(candidate, eligibility, "laboratorio")


def test_governance_snapshot_does_not_release_publication_barrier(tmp_path):
    from petroandes.catalog.api import Catalog
    from petroandes.catalog.store import profile_path

    with catalog(tmp_path) as store:
        with Catalog.open(tmp_path / "laboratorio/catalog.sqlite3", "laboratorio") as other:
            other.db.execute("PRAGMA busy_timeout=10")
            with governance_fence(policy(store), 0):
                assert store.db.in_transaction
                assert store.snapshot().revision == 0
                assert store.db.in_transaction
                with pytest.raises(sqlite3.OperationalError, match="locked"):
                    other.db.execute("BEGIN IMMEDIATE")
            other.db.execute("BEGIN IMMEDIATE")
            other.db.rollback()
        assert not store.db.in_transaction
