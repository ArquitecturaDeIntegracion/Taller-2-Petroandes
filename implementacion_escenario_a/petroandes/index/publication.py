"""Publicación local atómica bajo barrera de gobierno, sin conceder permisos."""
from contextlib import contextmanager

from petroandes.catalog.store import document_key
from petroandes.contracts.documents import Document, Fragment
from petroandes.extract.staging import record_digest
from .common import IndexUnavailable, context_data, digest, generation_id
from .dense import DenseOwner
from .generation import prepare, verify
from .projections import LEXICAL_VERSION
from .registry import Registry


def document_identity(document):
    return document_key(document), document.pdf_sha256


def select(stage, eligibility, profile):
    if stage.manifest["perfil"] != profile:
        raise IndexUnavailable("Staging y gobierno de perfiles distintos")
    allowed = {document_identity(doc) for doc in eligibility.documentos}
    available, selected = set(), []
    parent_map = {parent["parent_id"]: parent for parent in stage.parents}
    ids = set()
    for item in stage.records:
        fragment = Fragment.model_validate(item["fragment"])
        document = Document.model_validate(item["metadata"]["documento"])
        if document_identity(fragment) != document_identity(document):
            raise IndexUnavailable("Identidad documental incoherente")
        if fragment.chunk_id in ids or fragment.parent_id not in parent_map:
            raise IndexUnavailable("Fragmento duplicado o padre ausente")
        ids.add(fragment.chunk_id)
        available.add(document_identity(fragment))
        if document_identity(fragment) in allowed:
            selected.append(item)
    if not allowed.issubset(available):
        raise IndexUnavailable("Documento elegible sin staging de su hash actual")
    return sorted(selected, key=lambda item: item["fragment"]["chunk_id"])


@contextmanager
def governance_fence(policy, expected_revision):
    store = policy.catalog
    store.db.execute("BEGIN IMMEDIATE")
    try:
        if store.verify_revision() != expected_revision:
            raise IndexUnavailable("Gobierno cambió durante la preparación")
        yield policy.eligible()
        store.db.commit()
    except Exception:
        store.db.rollback()
        raise


class Publisher:
    def __init__(self, root, policy, encoder):
        root = root.resolve()
        self.root, self.policy, self.encoder = root, policy, encoder
        root.mkdir(parents=True, exist_ok=True)
        self.owner = DenseOwner(root / "qdrant")
        try:
            self.registry = Registry(root / "publications.sqlite3")
        except Exception:
            self.owner.close()
            raise

    def publish(self, stage, *, before_activate=None):
        eligibility = self.policy.eligible()
        records = select(stage, eligibility, self.policy.catalog.perfil)
        key = {"stage": stage.manifest["generation_id"], "perfil": self.policy.catalog.perfil,
            "revision_gobierno": eligibility.revision, "context": context_data(self.policy.context),
            "bundle_fingerprint": self.encoder.fingerprint, "lexical_version": LEXICAL_VERSION,
            "records_sha256": digest([record_digest(item) for item in records])}
        key["generation_id"] = generation_id(key)
        receipt, reused = prepare(self.root, self.owner, self.encoder, records, stage.parents, key,
                                  [item["embedding_input"] for item in records])
        if before_activate:
            before_activate()  # inyección de fallos/carreras; no expuesto a CLI/MCP
        with governance_fence(self.policy, eligibility.revision) as current:
            if select(stage, current, self.policy.catalog.perfil) != records:
                raise IndexUnavailable("Elegibilidad cambió antes de activar")
            folder = self.root / "generations" / key["generation_id"]
            verify(folder, receipt, self.owner, self.encoder.fingerprint)
            if select(stage, self.policy.eligible(), self.policy.catalog.perfil) != records:
                raise IndexUnavailable("Permiso venció durante la verificación de publicación")
            self.registry.activate(key["generation_id"], receipt)
        return {"generation_id": key["generation_id"], "perfil": key["perfil"],
                "governance_revision": eligibility.revision, "published_fragments": len(records),
                "eligible_documents": len(eligibility.documentos), "reused": reused,
                "collection": receipt["collection"]}

    def active(self):
        receipt = self.registry.active()
        key = receipt["key"]
        if key["context"] != context_data(self.policy.context) or key["perfil"] != self.policy.catalog.perfil:
            raise IndexUnavailable("Contexto del servicio distinto de la publicación")
        with governance_fence(self.policy, key["revision_gobierno"]) as current:
            folder = self.root / "generations" / key["generation_id"]
            manifest = verify(folder, receipt, self.owner, self.encoder.fingerprint)
            # No reutilizar una generación al vencer permisos, aunque no cambie la revisión.
            import json
            import sqlite3
            from contextlib import closing

            allowed = {document_identity(doc) for doc in current.documentos}
            with closing(sqlite3.connect((folder / "catalog.sqlite3").as_uri() + "?mode=ro", uri=True)) as db:
                for (payload,) in db.execute("SELECT payload FROM fragments"):
                    fragment = Fragment.model_validate(json.loads(payload)["fragment"])
                    if document_identity(fragment) not in allowed:
                        raise IndexUnavailable("Permiso vencido o revocado en generación activa")
        return manifest, receipt

    def close(self):
        self.registry.close()
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
