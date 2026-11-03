"""Mutaciones documentales internas; una huella nueva no hereda certificación."""
from petroandes.contracts.documents import Document
from petroandes.governance.models import Observation, Relation
from .store import document_key


def insert_document(db, doc, revision):
    key = document_key(doc)
    db.execute("INSERT INTO document_history VALUES (?,?,?)",
               (key, doc.pdf_sha256, doc.model_dump_json()))
    db.execute("INSERT INTO documents VALUES (?,?,?,?) ON CONFLICT(document_key) DO UPDATE SET "
               "pdf_sha256=excluded.pdf_sha256,payload=excluded.payload,"
               "registration_revision=excluded.registration_revision",
               (key, doc.pdf_sha256, doc.model_dump_json(), revision))


def validate_sources(db, evidence):
    for item in evidence:
        source = db.execute("SELECT pdf_sha256 FROM documents WHERE document_key=?",
                            (document_key(item.fuente),)).fetchone()
        if source != (item.pdf_sha256,):
            raise ValueError("La evidencia no corresponde a una fuente del catálogo")


def seed(store, documents, observations, relations):
    documents = tuple(Document.model_validate_json(item.model_dump_json()) for item in documents)
    observations = tuple(Observation.model_validate_json(item.model_dump_json()) for item in observations)
    relations = tuple(Relation.model_validate_json(item.model_dump_json()) for item in relations)

    def mutation(revision):
        if store.db.execute("SELECT count(*) FROM documents").fetchone()[0]:
            raise ValueError("La carga inicial requiere catálogo vacío")
        for doc in documents:
            insert_document(store.db, doc, revision)
        by_key = {document_key(doc): doc.pdf_sha256 for doc in documents}
        for observation in observations:
            key = document_key(observation.documento)
            if by_key.get(key) != observation.pdf_sha256:
                raise ValueError("Observación para otro documento/hash")
            validate_sources(store.db, observation.fuentes)
            store.db.execute("INSERT INTO observations VALUES (?,?,?,?)", (observation.observation_id,
                key, observation.pdf_sha256, observation.model_dump_json()))
        for relation in relations:
            validate_sources(store.db, (relation.evidencia,))
            store.db.execute("INSERT INTO relations VALUES (?,?)",
                             (relation.relation_id, relation.model_dump_json()))
        return True

    return store.change(0, "corpus.inicializado", {"documentos": len(documents),
                        "observaciones": len(observations), "relaciones": len(relations)}, mutation)


def put_document(store, document, expected_revision):
    doc = Document.model_validate_json(document.model_dump_json())

    def mutation(revision):
        row = store.db.execute("SELECT pdf_sha256,payload FROM documents WHERE document_key=?",
                               (document_key(doc),)).fetchone()
        if row == (doc.pdf_sha256, doc.model_dump_json()):
            return False
        history = store.db.execute("SELECT payload FROM document_history WHERE document_key=? AND pdf_sha256=?",
                                  (document_key(doc), doc.pdf_sha256)).fetchone()
        if history:
            if history[0] != doc.model_dump_json():
                raise ValueError("Metadatos diferentes para la misma identidad y huella")
            store.db.execute("UPDATE documents SET pdf_sha256=?,payload=?,registration_revision=? "
                             "WHERE document_key=?",
                             (doc.pdf_sha256, doc.model_dump_json(), revision, document_key(doc)))
        else:
            insert_document(store.db, doc, revision)
        return True

    return store.change(expected_revision, "documento.registrado", {"doc_id": doc.doc_id,
        "version_documental": doc.version_documental, "pdf_sha256": doc.pdf_sha256}, mutation)
