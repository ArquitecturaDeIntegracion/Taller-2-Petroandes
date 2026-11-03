"""Persistencia, aislamiento, carreras y fallos reales de SQLite."""
import sqlite3

import pytest

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import CatalogUnavailable, RevisionConflict
from f2_helpers import catalog, doc, policy, record


def test_missing_catalog_fails_without_creating_file(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(CatalogUnavailable):
        Catalog.open(missing, "baseline")
    assert not missing.exists()


def test_reopen_retains_state_history_and_pending_events(tmp_path):
    source = doc()
    path = tmp_path / "laboratorio/catalog.sqlite3"
    with catalog(tmp_path) as store:
        store.put_document(source, 0)
        store.apply_decision(record(source, 2), 1)
    with Catalog.open(path, "laboratorio") as reopened:
        assert policy(reopened).eligible().documentos == (source,)
        assert reopened.summary()["governance_revision"] == 2
        assert len(reopened.pending_events()) == 2


def test_profiles_and_decisions_are_isolated(tmp_path):
    with catalog(tmp_path, "baseline") as base, catalog(tmp_path) as lab:
        source = doc()
        base.put_document(source, 0)
        lab.put_document(source, 0)
        lab.apply_decision(record(source, 2), 1)
        assert policy(base).eligible().documentos == ()
        assert policy(lab).eligible().documentos == (source,)
        with pytest.raises(ValueError, match="otro perfil"):
            base.apply_decision(record(source, 2), 1)
    with pytest.raises(CatalogUnavailable):
        Catalog.open(tmp_path / "laboratorio/catalog.sqlite3", "baseline")


def test_failure_writing_event_rolls_back_decision_and_revision(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.db.execute("CREATE TRIGGER fail_event BEFORE INSERT ON events "
                         "BEGIN SELECT RAISE(ABORT,'fallo sintetico de outbox'); END")
        with pytest.raises(sqlite3.IntegrityError, match="outbox"):
            store.apply_decision(record(source, 2), 1)
        assert store.verify_revision() == 1
        assert store.snapshot().decisiones == ()
        assert len(store.pending_events()) == 1
        assert policy(store).eligible().documentos == ()


def test_stale_writer_is_rejected_and_same_decision_is_idempotent(tmp_path):
    path = tmp_path / "laboratorio/catalog.sqlite3"
    with catalog(tmp_path) as first, Catalog.open(path, "laboratorio") as second:
        source = doc()
        first.put_document(source, 0)
        with pytest.raises(RevisionConflict):
            second.put_document(doc("OTRO"), 0)
        entry = record(source, 2)
        first.apply_decision(entry, 1)
        assert first.apply_decision(entry, 2) == 2
        assert first.put_document(source, 2) == 2
        assert len(first.pending_events()) == 2


@pytest.mark.parametrize("sql", [
    "UPDATE metadata SET revision=99", "DELETE FROM events WHERE revision=1",
    "PRAGMA user_version=999", "UPDATE documents SET pdf_sha256='hash-corrupto'",
    "UPDATE decisions SET payload='{}'",
])
def test_incoherent_catalog_never_expands_access(tmp_path, sql):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.apply_decision(record(source, 2), 1)
        store.db.execute(sql)
        with pytest.raises(CatalogUnavailable):
            policy(store).eligible()


def test_historical_decision_cannot_be_overwritten(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.apply_decision(record(source, 2), 1)
        with pytest.raises(ValueError, match="histórica"):
            store.apply_decision(record(source, 2, estado="excluido"), 2)
        assert store.verify_revision() == 2


def test_read_only_catalog_supports_policy_but_rejects_writes(tmp_path):
    path = tmp_path / "laboratorio/catalog.sqlite3"
    with catalog(tmp_path) as store:
        store.put_document(doc(), 0)
    with Catalog.open(path, "laboratorio", read_only=True) as readonly:
        assert policy(readonly).eligible().documentos == ()
        with pytest.raises(sqlite3.OperationalError):
            readonly.put_document(doc("OTRO"), 1)
        assert readonly.summary()["documentos"] == 1
