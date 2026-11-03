"""Decisiones internas con revisión esperada; no hay importador de aprobaciones MCP."""
from petroandes.governance.models import Conflict, DecisionRecord
from .store import document_key


def apply_decision(store, record, expected_revision):
    record = DecisionRecord.model_validate_json(record.model_dump_json())
    decision = record.decision
    if decision.perfil != store.perfil:
        raise ValueError("Decisión de otro perfil")

    def mutation(revision):
        previous = store.db.execute("SELECT payload FROM decisions WHERE decision_id=?",
                                    (decision.decision_id,)).fetchone()
        if previous:
            if previous[0] != record.model_dump_json():
                raise ValueError("No sobrescribir una decisión histórica")
            return False
        doc = store.db.execute("SELECT pdf_sha256 FROM documents WHERE document_key=?",
                               (document_key(decision),)).fetchone()
        if doc != (decision.pdf_sha256,):
            raise ValueError("La decisión no corresponde al hash actual")
        if decision.revision_gobierno != revision:
            raise ValueError("Revisión de decisión distinta de la transacción")
        store.db.execute("INSERT INTO decisions VALUES (?,?,?,?)", (decision.decision_id,
            document_key(decision), revision, record.model_dump_json()))
        return True

    return store.change(expected_revision, "gobierno.decision", {"decision_id": decision.decision_id,
        "document_key": document_key(decision), "estado": decision.estado}, mutation)


def add_conflict(store, conflict, expected_revision):
    conflict = Conflict.model_validate_json(conflict.model_dump_json())

    def mutation(_revision):
        for doc in conflict.documentos:
            if not store.db.execute("SELECT 1 FROM documents WHERE document_key=?",
                                     (document_key(doc),)).fetchone():
                raise ValueError("Conflicto para documento ausente")
        store.db.execute("INSERT INTO conflicts VALUES (?,?,NULL)",
                         (conflict.conflict_id, conflict.model_dump_json()))
        return True

    return store.change(expected_revision, "gobierno.conflicto", conflict.model_dump(mode="json"), mutation)


def resolve_conflict(store, conflict_id, reviewer, expected_revision):
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("La resolución exige responsable humano explícito")

    def mutation(revision):
        row = store.db.execute("SELECT resolved_revision FROM conflicts WHERE conflict_id=?",
                               (conflict_id,)).fetchone()
        if row is None:
            raise ValueError("Conflicto desconocido")
        if row[0] is not None:
            return False
        store.db.execute("UPDATE conflicts SET resolved_revision=? WHERE conflict_id=?",
                         (revision, conflict_id))
        return True

    return store.change(expected_revision, "gobierno.conflicto_resuelto",
                        {"conflict_id": conflict_id, "revisor_humano": reviewer}, mutation)
