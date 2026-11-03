"""Política común previa a recuperación, obtención directa y expansión de contexto."""
from datetime import datetime, timezone

from petroandes.catalog.store import CatalogUnavailable, document_key
from .models import Eligibility, ServiceContext


def utcnow():
    return datetime.now(timezone.utc)


class EligibilityService:
    def __init__(self, catalog, context: ServiceContext, *, clock=utcnow):
        self.catalog = catalog
        self.context = ServiceContext.model_validate_json(context.model_dump_json())
        self.clock = clock  # inyección interna para pruebas; nunca un parámetro MCP

    def eligible(self):
        snapshot = self.catalog.snapshot()
        now = self.clock()
        if now.tzinfo is None or now.utcoffset() is None:
            raise CatalogUnavailable("Reloj del servicio sin zona horaria")
        for conflict in snapshot.conflictos:
            if (conflict.ambito == self.context.ambito and conflict.uso == self.context.uso
                    and conflict.effective_from <= now
                    and (conflict.effective_to is None or now < conflict.effective_to)):
                return Eligibility(snapshot.revision, (), "conflicto_documental", now)
        latest = {document_key(row.decision): row for row in snapshot.decisiones}
        registrations = dict(snapshot.registros)
        excluded = {(document_key(row.documento), row.pdf_sha256) for row in snapshot.observaciones
                    if row.estado == "excluido"}
        documents = []
        for doc in snapshot.documentos:
            key = document_key(doc)
            record = latest.get(key)
            if not record or (key, doc.pdf_sha256) in excluded:
                continue
            decision = record.decision
            if (decision.estado != "certificado" or decision.pdf_sha256 != doc.pdf_sha256
                    or record.autenticidad != "verificada"
                    or decision.revision_gobierno < registrations[key]):
                continue
            if (decision.revisado_en > now or decision.effective_from > now
                    or (decision.effective_to is not None and now >= decision.effective_to)):
                continue
            if (self.context.ambito not in decision.ambitos or self.context.uso not in decision.usos
                    or not self.context.grupos.intersection(decision.grupos)):
                continue
            documents.append(doc)
        return Eligibility(snapshot.revision, tuple(documents),
                           "autorizado" if documents else "sin_evidencia_autorizada", now)

    def authorize(self, reference):
        result = self.eligible()
        matches = tuple(doc for doc in result.documentos
                        if document_key(doc) == document_key(reference)
                        and doc.pdf_sha256 == reference.pdf_sha256)
        return Eligibility(result.revision, matches,
                           "autorizado" if matches else "evidencia_no_autorizada", result.evaluado_en)

    def revalidate(self, revision):
        return self.catalog.verify_revision() == revision
