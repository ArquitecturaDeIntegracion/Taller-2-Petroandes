"""Elegibilidad común con catálogo SQLite real y decisiones exclusivamente sintéticas."""
from datetime import timedelta

import pytest
from pydantic import ValidationError

from petroandes.catalog.store import CatalogUnavailable, RevisionConflict
from petroandes.contracts.common import Scope
from petroandes.governance.models import Conflict, DecisionRecord, Identity
from f2_helpers import NOW, SCOPE, catalog, context, doc, policy, record


def test_no_decision_is_not_authorized(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        assert policy(store).eligible().documentos == ()
        assert policy(store).authorize(source).motivo == "evidencia_no_autorizada"


@pytest.mark.parametrize("changes", [
    {"estado": "pendiente"}, {"estado": "excluido"},
    {"effective_to": NOW}, {"effective_from": NOW + timedelta(hours=1)},
    {"revisado_en": NOW + timedelta(days=1)},
    {"ambitos": (Scope(tipo="activo", identificador="OTRO"),)},
    {"usos": ("evidencia_historica",)}, {"grupos": ("OTRO-GRUPO",)},
])
def test_ineligible_decisions_never_enter_candidates(tmp_path, changes):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.apply_decision(record(source, 2, **changes), 1)
        assert policy(store).eligible().documentos == ()
        assert policy(store).authorize(source).documentos == ()


def test_authorized_recommendation_is_not_operating_instruction(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.apply_decision(record(source, 2), 1)
        assert policy(store).eligible().documentos == (source,)
        assert policy(store).authorize(source).documentos == (source,)
        assert policy(store, context(uso="instruccion_operativa")).eligible().documentos == ()
        assert policy(store, context(grupos=frozenset(["OTRO"])) ).eligible().documentos == ()


def test_authenticity_and_unsafe_content_remain_separate(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        authorization = record(source, 2)
        unverified = DecisionRecord(decision=authorization.decision, supuesto=authorization.supuesto)
        store.apply_decision(unverified, 1)
        assert policy(store).eligible().documentos == ()
        assert store.snapshot().decisiones[0].contenido_no_confiable is True


def test_hash_change_and_technical_rollback_do_not_restore_approval(tmp_path):
    with catalog(tmp_path) as store:
        old = doc()
        store.put_document(old, 0)
        store.apply_decision(record(old, 2), 1)
        old_revision = policy(store).eligible().revision
        changed = doc(content="PDF cambiado")
        store.put_document(changed, 2)
        assert policy(store).eligible().documentos == ()
        assert not policy(store).revalidate(old_revision)
        with pytest.raises(ValueError, match="hash actual"):
            store.apply_decision(record(old, 4), 3)
        store.put_document(old, 3)
        assert policy(store).eligible().documentos == ()
        assert store.summary()["clasificacion"]["pendiente"] == 1


def test_revocation_keeps_history_and_prevents_direct_access(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.apply_decision(record(source, 2), 1)
        store.apply_decision(record(source, 3, estado="excluido"), 2)
        assert policy(store).eligible().documentos == ()
        assert policy(store).authorize(source).documentos == ()
        assert len(store.snapshot().decisiones) == 2
        assert len(store.pending_events()) == 3


def test_conflict_blocks_entire_scope_until_explicit_resolution(tmp_path):
    with catalog(tmp_path) as store:
        first, second = doc(), doc("OTRO-SINTETICO")
        store.put_document(first, 0)
        store.put_document(second, 1)
        store.apply_decision(record(first, 3), 2)
        store.apply_decision(record(second, 4), 3)
        references = tuple(Identity(doc_id=item.doc_id, version_documental=item.version_documental)
                           for item in (first, second))
        conflict = Conflict(conflict_id="FIXTURE-CONFLICT", documentos=references,
            ambito=SCOPE, uso="recomendacion", fundamento="Incompatibilidad sintética",
            registrado_por="REVISOR-FICTICIO", effective_from=NOW - timedelta(days=1))
        store.add_conflict(conflict, 4)
        assert policy(store).eligible().motivo == "conflicto_documental"
        assert policy(store).authorize(first).documentos == ()
        store.resolve_conflict(conflict.conflict_id, "REVISOR-FICTICIO", 5)
        assert len(policy(store).eligible().documentos) == 2


def test_naive_clock_is_unavailable(tmp_path):
    with catalog(tmp_path) as store:
        with pytest.raises(CatalogUnavailable):
            policy(store, at=NOW.replace(tzinfo=None)).eligible()


def test_open_period_must_be_explicit_and_is_eligible_when_approved(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        with pytest.raises(ValidationError, match="decisión expresa"):
            record(source, 2, effective_to=None)
        store.apply_decision(record(source, 2, effective_to=None,
                                    intervalo_abierto_expreso=True), 1)
        assert policy(store).eligible().documentos == (source,)


def test_revocation_cannot_be_bypassed_by_a_historical_test_clock(tmp_path):
    with catalog(tmp_path) as store:
        source = doc()
        store.put_document(source, 0)
        store.apply_decision(record(source, 2), 1)
        store.apply_decision(record(source, 3, estado="excluido"), 2)
        assert policy(store, at=NOW - timedelta(hours=2)).eligible().documentos == ()
