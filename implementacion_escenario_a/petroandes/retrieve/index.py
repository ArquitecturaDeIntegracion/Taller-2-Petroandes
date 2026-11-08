"""Abrir una generación F4 sin republicar ni usar el catálogo como proyección."""
import json
import sqlite3
from contextlib import closing, contextmanager

from petroandes.contracts.documents import Document, Fragment
from petroandes.index.common import IndexUnavailable, context_data
from petroandes.index.dense import DenseOwner
from petroandes.index.generation import verify
from petroandes.index.projections import LEXICAL_VERSION
from petroandes.index.publication import document_identity
from petroandes.index.registry import Registry


class StaleGeneration(IndexUnavailable):
    pass


@contextmanager
def open_generation(root, policy, eligibility, encoder):
    with closing(Registry(root / "publications.sqlite3", read_only=True)) as registry:
        receipt = registry.active()
        key = receipt["key"]
        if (key["context"] != context_data(policy.context) or key["perfil"] != policy.catalog.perfil
                or key["lexical_version"] != LEXICAL_VERSION):
            raise IndexUnavailable("Contexto, perfil o tokenización distintos de la publicación")
        if key["revision_gobierno"] != eligibility.revision:
            raise StaleGeneration("La generación activa corresponde a otra revisión")
        if not (root / "qdrant").is_dir():
            raise IndexUnavailable("Almacén Qdrant ausente")
        folder = root / "generations" / key["generation_id"]
        with closing(DenseOwner(root / "qdrant")) as owner:
            manifest = verify(folder, receipt, owner, encoder.fingerprint)
            yield owner, manifest, receipt["collection"], folder


def authorized_records(path, eligibility):
    allowed = {document_identity(doc): doc for doc in eligibility.documentos}
    records = {}
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        for (payload,) in db.execute("SELECT payload FROM fragments ORDER BY chunk_id"):
            record = json.loads(payload)
            fragment = Fragment.model_validate(record["fragment"])
            document = allowed.get(document_identity(fragment))
            if document is None:
                continue
            if Document.model_validate(record["metadata"]["documento"]) != document:
                raise IndexUnavailable("Documento publicado distinto del registro vigente")
            records[fragment.chunk_id] = (fragment, record)
    if not set(allowed).issubset(document_identity(part) for part, _ in records.values()):
        raise IndexUnavailable("Faltan documentos elegibles en la generación activa")
    return records
