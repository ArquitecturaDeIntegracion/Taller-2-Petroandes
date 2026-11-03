"""Lectura consistente del registro; corrupción o revisión incompleta cierran acceso."""
import json
import sqlite3

from pydantic import ValidationError
from petroandes.contracts.documents import Document
from petroandes.governance.models import Conflict, DecisionRecord, Observation, Snapshot
from .store import CatalogUnavailable, document_key


def read_snapshot(store):
    owns_transaction = not store.db.in_transaction
    if owns_transaction:
        store.db.execute("BEGIN")
    try:
        revision = store.verify_revision()
        documents, registrations = [], []
        if store.db.execute("PRAGMA foreign_key_check").fetchone():
            raise CatalogUnavailable("Referencias del catálogo incoherentes")
        for key, digest, payload, registered in store.db.execute("SELECT * FROM documents ORDER BY document_key"):
            doc = Document.model_validate_json(payload)
            if (document_key(doc) != key or doc.pdf_sha256 != digest
                    or not 1 <= registered <= revision):
                raise CatalogUnavailable("Identidad documental incoherente")
            documents.append(doc)
            registrations.append((key, registered))
        observations = []
        for oid, key, digest, payload in store.db.execute("SELECT * FROM observations"):
            item = Observation.model_validate_json(payload)
            if (item.observation_id != oid or document_key(item.documento) != key
                    or item.pdf_sha256 != digest):
                raise CatalogUnavailable("Observación documental incoherente")
            observations.append(item)
        decisions = []
        for did, key, rev, payload in store.db.execute("SELECT * FROM decisions ORDER BY revision"):
            item = DecisionRecord.model_validate_json(payload)
            if (item.decision.decision_id != did or document_key(item.decision) != key
                    or item.decision.revision_gobierno != rev or rev > revision
                    or item.decision.perfil != store.perfil):
                raise CatalogUnavailable("Decisión de gobierno incoherente")
            decisions.append(item)
        conflicts = tuple(Conflict.model_validate_json(row[0]) for row in store.db.execute(
            "SELECT payload FROM conflicts WHERE resolved_revision IS NULL"))
        result = Snapshot(store.perfil, revision, tuple(documents), tuple(registrations), tuple(observations),
                          tuple(decisions), conflicts)
        if owns_transaction:
            store.db.commit()
        return result
    except (sqlite3.Error, ValidationError, ValueError, KeyError) as exc:
        if owns_transaction:
            store.db.rollback()
        raise CatalogUnavailable("Registro de gobierno inválido; no ampliar la consulta") from exc
    except Exception:
        if owns_transaction:
            store.db.rollback()
        raise


def summary(store):
    snapshot = read_snapshot(store)
    decisions = {document_key(row.decision): row.decision for row in snapshot.decisiones}
    registrations = dict(snapshot.registros)
    counts = {"pendiente": 0, "excluido": 0, "certificado": 0}
    for doc in snapshot.documentos:
        matching = [item for item in snapshot.observaciones if document_key(item.documento)
                    == document_key(doc) and item.pdf_sha256 == doc.pdf_sha256]
        excluded = any(item.estado == "excluido" for item in matching)
        decision = decisions.get(document_key(doc))
        state = "excluido" if excluded else "pendiente"
        if (not excluded and decision and decision.pdf_sha256 == doc.pdf_sha256
                and decision.revision_gobierno >= registrations[document_key(doc)]):
            state = decision.estado
        counts[state] += 1
    return {"perfil": snapshot.perfil, "governance_revision": snapshot.revision,
            "documentos": len(snapshot.documentos), "clasificacion": counts,
            "decisiones_registradas": len(snapshot.decisiones),
            "conflictos_abiertos": len(snapshot.conflictos),
            "eventos_pendientes": len(store.pending_events())}
