"""La exclusión por sustitución y su evento se aplican juntos."""
import sqlite3

import pytest

from f2_helpers import catalog, doc, policy, record
from petroandes.catalog.substitution import substitute
from petroandes.governance.baseline import identity
from petroandes.governance.models import Observation, PdfEvidence, Relation


def test_substitution_rejects_partial_commit_and_does_not_authorize_successor(tmp_path):
    previous, successor = doc("SINTETICO-A"), doc("SINTETICO-B")
    source = PdfEvidence(fuente=identity(successor), pdf_sha256=successor.pdf_sha256,
                         section_id="encabezado", pagina=1, cita="Reemplaza SINTETICO-A")
    observation = Observation(observation_id="f10-exclusion", documento=identity(previous),
                              pdf_sha256=previous.pdf_sha256, estado="excluido",
                              fundamento="Fixture de sustitución", fuentes=(source,))
    relation = Relation(relation_id="f10-sustitucion", tipo="reemplaza", desde=identity(successor),
                        hacia=identity(previous), evidencia=source)
    with catalog(tmp_path) as store:
        store.put_document(previous, 0)
        store.put_document(successor, 1)
        store.apply_decision(record(previous, 3), 2)
        store.db.execute("CREATE TRIGGER fail BEFORE INSERT ON events "
                         "BEGIN SELECT RAISE(ABORT,'fallo inyectado'); END")
        with pytest.raises(sqlite3.IntegrityError):
            substitute(store, observation, relation, "Revisión ficticia", 3)
        assert store.verify_revision() == 3 and store.snapshot().observaciones == ()
        assert store.db.execute("SELECT count(*) FROM relations").fetchone() == (0,)
        assert policy(store).eligible().documentos == (previous,)
        store.db.execute("DROP TRIGGER fail")
        assert substitute(store, observation, relation, "Revisión ficticia", 3) == 4
        assert policy(store).eligible().documentos == ()
        assert store.summary()["clasificacion"] == {"pendiente": 1, "excluido": 1, "certificado": 0}
        assert substitute(store, observation, relation, "Revisión ficticia", 4) == 4
        assert [item[:2] for item in store.pending_events()][-1] == (4, "documento.sustituido")
