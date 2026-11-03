"""Integración PDF->evidencia->SQLite real; no hay autorizaciones académicas."""
from petroandes.catalog.api import Catalog
from petroandes.governance.baseline import EXCLUSIONS, load_baseline
from f2_helpers import policy, record


def test_real_baseline_has_four_exclusions_fifteen_pending_and_no_approvals(tmp_path):
    documents, observations, relations = load_baseline()
    path = tmp_path / "baseline.sqlite3"
    with Catalog.create(path, "baseline") as store:
        store.seed(documents, observations, relations)
        assert store.summary()["clasificacion"] == {"pendiente": 15, "excluido": 4, "certificado": 0}
        assert store.summary()["decisiones_registradas"] == 0
        assert store.verify_revision() == 1
        assert len(store.pending_events()) == 1
        assert policy(store).eligible().documentos == ()
        for document in documents:
            assert policy(store).authorize(document).documentos == ()
    excluded = {(item.documento.doc_id, item.documento.version_documental)
                for item in observations if item.estado == "excluido"}
    assert excluded == set(EXCLUSIONS)
    assert all(item.fuentes and item.fuentes[0].pagina == 1
               for item in observations if item.estado == "excluido")
    assert any(item.doc_id == "COM-PRV-0134" for item in documents)
    assert all(item.version_documental is None for item in documents if item.tipo == "resolucion")


def test_missing_predecessor_is_only_a_relation_not_a_twentieth_document(tmp_path):
    documents, observations, relations = load_baseline()
    predecessor = [item.hacia for item in relations
                   if item.desde.doc_id == "MAN-OPE-001"]
    assert predecessor[0].version_documental == "2"
    assert not any(item.doc_id == "MAN-OPE-001" and item.version_documental == "2"
                   for item in documents)
    assert any(item.tipo == "deroga" for item in relations)
    assert any(item.desde.doc_id == "PRO-SEG-015" and item.hacia.doc_id == "PRO-SEG-009"
               for item in relations)


def test_documentary_exclusion_is_not_overridden_by_a_synthetic_certificate(tmp_path):
    documents, observations, relations = load_baseline()
    excluded = next(item for item in documents if item.doc_id == "PRO-SEG-009")
    with Catalog.create(tmp_path / "lab.sqlite3", "laboratorio") as store:
        store.seed(documents, observations, relations)
        store.apply_decision(record(excluded, 2), 1)
        assert policy(store).authorize(excluded).documentos == ()
