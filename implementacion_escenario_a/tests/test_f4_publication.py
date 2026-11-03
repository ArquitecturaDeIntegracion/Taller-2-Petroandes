"""Qdrant/E5 reales y SQLite: publicación, coherencia, persistencia y exclusiones."""
import json
import sqlite3
import subprocess
import sys
from datetime import timedelta

import numpy as np
import pytest

from petroandes.embeddings.encoder import BundleMismatch, E5Encoder, EncodedQuery, validate_vectors
from petroandes.index.common import IndexUnavailable
from petroandes.index.dense import DenseOwner
from petroandes.index.projections import lexical_search, tokens
from petroandes.index.publication import Publisher
from f2_helpers import NOW, catalog, context, doc, policy, record
from f4_helpers import stage_fixture


@pytest.fixture(scope="module")
def encoder():
    return E5Encoder()


def test_real_e5_contract_and_rejections(encoder):
    assert encoder.manual_pooling_delta < 1e-5
    query = encoder.query("¿Qué registra la ficha?", expected_fingerprint=encoder.fingerprint)
    validate_vectors(np.asarray([query.vector]), 1)
    with pytest.raises(BundleMismatch):
        encoder.query("Pregunta", expected_fingerprint="otro-bundle-misma-dimension")
    with pytest.raises(ValueError):
        encoder.encode_passages(["query: tipo incorrecto"])
    with pytest.raises(ValueError):
        encoder.encode_passages(["passage: " + "dato " * 600])
    for vector in (np.zeros((1, 384)), np.full((1, 384), np.nan), np.ones((1, 383))):
        with pytest.raises(ValueError):
            validate_vectors(vector, 1)


def test_real_publish_reopen_idempotence_and_prefilters(tmp_path, encoder):
    root = tmp_path / "indexes"
    with catalog(tmp_path) as store:
        stage = stage_fixture(store, encoder)
        with Publisher(root, policy(store), encoder) as publisher:
            first = publisher.publish(stage)
            assert first["published_fragments"] == first["eligible_documents"] == 1
            assert not first["reused"]
            second = publisher.publish(stage)
            assert second == first | {"reused": True}
            manifest, receipt = publisher.active()
            ids = set(manifest.fragmentos)
            query = encoder.query("P-101", expected_fingerprint=encoder.fingerprint)
            kwargs = dict(generation=manifest.generation_id, revision=manifest.revision_gobierno,
                          fingerprint=encoder.fingerprint)
            assert len(publisher.owner.search(receipt["collection"], query, ids, **kwargs)) == 1
            assert publisher.owner.search(receipt["collection"], query, set(), **kwargs) == []
            assert publisher.owner.search(receipt["collection"], query, ids, **(kwargs | {"revision": 999})) == []
            with pytest.raises(BundleMismatch):
                publisher.owner.search(receipt["collection"], EncodedQuery("otro", query.vector), ids, **kwargs)
            lexical = root / "generations" / manifest.generation_id / "lexical.sqlite3"
            assert lexical_search(lexical, "P-101", ids)[0][0] in ids
            assert lexical_search(lexical, "P-101", set()) == []
            with pytest.raises(RuntimeError):
                DenseOwner(root / "qdrant")
        with Publisher(root, policy(store), encoder) as reopened:
            saved, _ = reopened.active()
            assert saved == manifest
            assert reopened.publish(stage)["reused"]
        child = subprocess.run([sys.executable, "-c", '''
import json, sys
from pathlib import Path
from petroandes.index.dense import DenseOwner
from petroandes.index.generation import verify
from petroandes.index.registry import Registry
root = Path(sys.argv[1])
registry = Registry(root / "publications.sqlite3")
owner = DenseOwner(root / "qdrant")
try:
    receipt = registry.active()
    key = receipt["key"]
    manifest = verify(root / "generations" / key["generation_id"], receipt, owner, key["bundle_fingerprint"])
    assert len(manifest.fragmentos) == 1
    print("persistencia-no-vacia-verificada-en-otro-proceso")
finally:
    registry.close()
    owner.close()
''', str(root)], capture_output=True, text=True, timeout=60)
        assert child.returncode == 0, child.stderr
        assert "persistencia-no-vacia" in child.stdout
        assert tokens("COM-PRV-0134 P-101 2026 v1.2") == ["com-prv-0134", "p-101", "2026", "v1.2"]


def test_revoke_hash_change_and_expiration_fail_closed(tmp_path, encoder):
    with catalog(tmp_path) as store:
        stage = stage_fixture(store, encoder)
        with Publisher(tmp_path / "index", policy(store), encoder) as publisher:
            publisher.publish(stage)
            publisher.policy = policy(store, at=NOW + timedelta(days=2))
            with pytest.raises(IndexUnavailable, match="vencido"):
                publisher.active()
            publisher.policy = policy(store)
            store.apply_decision(record(doc("SINTETICO-A"), 4, estado="pendiente"), 3)
            with pytest.raises(IndexUnavailable, match="Gobierno"):
                publisher.active()
            empty = publisher.publish(stage)
            assert empty["published_fragments"] == 0
            assert publisher.active()[0].fragmentos == ()
            changed = doc("SINTETICO-A", content="PDF cambiado")
            store.put_document(changed, 4)
            assert policy(store).eligible().documentos == ()
            assert publisher.publish(stage)["published_fragments"] == 0
            store.apply_decision(record(changed, 6), 5)
            with pytest.raises(IndexUnavailable, match="hash actual"):
                publisher.publish(stage)


def test_partial_and_race_do_not_activate(tmp_path, encoder):
    with catalog(tmp_path) as store:
        stage = stage_fixture(store, encoder)
        with Publisher(tmp_path / "index", policy(store), encoder) as publisher:
            first = publisher.publish(stage)
            def revoke():
                store.apply_decision(record(doc("SINTETICO-A"), 4, estado="pendiente"), 3)
            with pytest.raises(IndexUnavailable):
                publisher.publish(stage, before_activate=revoke)
            assert publisher.registry.active()["key"]["generation_id"] == first["generation_id"]
            def corrupt():
                for path in (tmp_path / "index/generations").glob("*/lexical.sqlite3"):
                    path.write_bytes(b"parcial")
            with pytest.raises((IndexUnavailable, sqlite3.Error)):
                publisher.publish(stage, before_activate=corrupt)
            assert publisher.registry.active()["key"]["generation_id"] == first["generation_id"]


def test_registry_failure_rolls_back_and_context_mismatch(tmp_path, encoder):
    with catalog(tmp_path) as store:
        stage = stage_fixture(store, encoder)
        with Publisher(tmp_path / "index", policy(store), encoder) as publisher:
            first = publisher.publish(stage)
            store.apply_decision(record(doc("SINTETICO-A"), 4, estado="pendiente"), 3)
            publisher.registry.db.execute("CREATE TRIGGER fail BEFORE UPDATE ON active BEGIN SELECT RAISE(ABORT,'fallo'); END")
            with pytest.raises(sqlite3.IntegrityError):
                publisher.publish(stage)
            assert publisher.registry.active()["key"]["generation_id"] == first["generation_id"]
            assert publisher.registry.db.execute("SELECT count(*) FROM generations").fetchone()[0] == 1
            publisher.registry.db.execute("DROP TRIGGER fail")
            publisher.publish(stage)
            publisher.policy = policy(store, ctx=context(grupos=frozenset(["OTRO"])))
            with pytest.raises(IndexUnavailable, match="Contexto"):
                publisher.active()
