"""Lotes aislados sobre PDF reales; nunca modifican los catálogos persistentes."""
import sqlite3
import shutil
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import RevisionConflict
from petroandes.contracts.common import Scope
from petroandes.governance.administration import ApprovalRequest, load_request
from petroandes.governance.baseline import load_baseline
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.governance.registration import register
from petroandes.paths import APP_ROOT, PROJECT_ROOT

FIXTURE_NOW = datetime.fromisoformat("2026-11-15T12:00:00-05:00")
REQUEST = APP_ROOT / "config/admin/lab-20261103/request/request.json"


def seeded(tmp_path, profile="laboratorio"):
    store = Catalog.create(tmp_path / "catalog.sqlite3", profile)
    store.seed(*load_baseline())
    return store


def policy(store, *, usage="evidencia_historica", group="LAB_REVISION", scope="corpus_revision", at=FIXTURE_NOW):
    context = ServiceContext(identidad="SONDA-FICTICIA", grupos=frozenset([group]),
        ambito=Scope(tipo="general", identificador=scope), uso=usage)
    return EligibilityService(store, context, clock=lambda: at)


def test_individual_decisions_events_and_period(tmp_path):
    request = load_request(REQUEST)
    with seeded(tmp_path) as store:
        records, reused = register(store, request, clock=lambda: FIXTURE_NOW)
        assert not reused and len(records) == 12
        assert store.summary()["clasificacion"] == {"certificado": 12, "pendiente": 3, "excluido": 4}
        assert store.verify_revision() == len(store.pending_events()) == 13
        assert [r.decision.revision_gobierno for r in records] == list(range(2, 14))
        assert all(r.decision.revisado_en == r.decision.effective_from == FIXTURE_NOW for r in records)
        assert len(policy(store).eligible().documentos) == 12
        assert len(policy(store, usage="instruccion_operativa").eligible().documentos) == 5
        assert len(policy(store, usage="referencia_normativa").eligible().documentos) == 2
        assert len(policy(store, usage="recomendacion").eligible().documentos) == 2
        assert len(policy(store, usage="inspeccion_no_confiable").eligible().documentos) == 1
        assert len(policy(store, usage="especificacion_activo").eligible().documentos) == 1
        assert policy(store, usage="limite_diseno").eligible().documentos == ()
        for changes in ({"group": "OTRO"}, {"scope": "OTRO"}, {"at": request.effective_to},
                        {"at": FIXTURE_NOW - timedelta(microseconds=1)}):
            assert policy(store, **changes).eligible().documentos == ()
        same, reused = register(store, request, clock=lambda: FIXTURE_NOW + timedelta(hours=1))
        assert reused and same == records and store.verify_revision() == 13


def test_sql_failure_rolls_back_all_twelve_decisions_and_events(tmp_path):
    with seeded(tmp_path) as store:
        store.db.execute("""CREATE TRIGGER fail BEFORE INSERT ON decisions WHEN NEW.revision=5
            BEGIN SELECT RAISE(ABORT,'fallo inducido'); END""")
        with pytest.raises(sqlite3.IntegrityError):
            register(store, load_request(REQUEST), clock=lambda: FIXTURE_NOW)
        assert store.verify_revision() == len(store.pending_events()) == 1
        assert store.summary()["decisiones_registradas"] == 0


@pytest.mark.parametrize("field,value", [("revisor_humano", "TODO"), ("perfil", "baseline"),
    ("revisor_humano", ""), ("simulacion_academica", False), ("effective_from", "2020-01-01T00:00:00Z")])
def test_invalid_or_retroactive_input_rejected(field, value):
    data = load_request(REQUEST).model_dump(mode="json") | {field: value}
    with pytest.raises(ValidationError):
        ApprovalRequest.model_validate(data)


def test_wrong_profile_exclusion_duplicate_and_expired_request(tmp_path):
    request = load_request(REQUEST)
    with seeded(tmp_path, "baseline") as base:
        with pytest.raises(ValueError, match="baseline"):
            register(base, request)
        assert base.verify_revision() == 1
    with seeded(tmp_path / "lab") as store:
        bad_spec = request.documentos[0].model_copy(update={"doc_id": "PRO-MED-007", "version_documental": "1"})
        with pytest.raises(ValueError, match="excluido"):
            register(store, request.model_copy(update={"documentos": (bad_spec,) + request.documentos[1:]}))
        with pytest.raises(ValidationError):
            register(store, request.model_copy(update={"documentos": request.documentos * 2}))
        with pytest.raises(ValueError, match="vencido"):
            register(store, request, clock=lambda: request.effective_to)
        assert store.verify_revision() == 1


def test_changed_pdf_prevents_every_decision(tmp_path, monkeypatch):
    from petroandes.governance import registration

    for document in load_baseline()[0]:
        relative = document.pdf_uri[8:]
        target = tmp_path / "project" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT_ROOT / relative, target)
    target = tmp_path / "project/corpus/pdf/02_procedimientos/PRO-HSE-003_v4.pdf"
    with target.open("ab") as output:
        output.write(b"cambio-controlado-solo-en-copia")
    monkeypatch.setattr(registration, "PROJECT_ROOT", tmp_path / "project")
    with seeded(tmp_path / "db") as store:
        with pytest.raises(ValueError, match="PDF cambió"):
            register(store, load_request(REQUEST), clock=lambda: FIXTURE_NOW)
        assert store.verify_revision() == 1


def test_replay_does_not_reverse_newer_revocation(tmp_path):
    request = load_request(REQUEST)
    with seeded(tmp_path) as store:
        records, _ = register(store, request, clock=lambda: FIXTURE_NOW)
        old = records[0]
        revoked = old.model_copy(update={"decision": old.decision.model_copy(update={
            "decision_id": "REVOCACION-FICTICIA", "estado": "pendiente", "revision_gobierno": 14})})
        store.apply_decision(revoked, 13)
        _, reused = register(store, request, clock=lambda: FIXTURE_NOW)
        assert reused and store.verify_revision() == 14
        assert len(policy(store).eligible().documentos) == 11


def test_authorization_hash_and_revision_fence(tmp_path):
    request = load_request(REQUEST)
    with seeded(tmp_path) as store:
        altered = request.model_copy(update={"autorizacion": request.autorizacion.model_copy(
            update={"sha256": "0" * 64})})
        with pytest.raises(ValueError, match="autorización"):
            register(store, altered)
        with pytest.raises(RevisionConflict):
            register(store, request.model_copy(update={"expected_revision": 2}))
        assert store.verify_revision() == 1
