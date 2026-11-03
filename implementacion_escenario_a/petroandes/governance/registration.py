"""Doce decisiones individuales o ninguna: validación previa y commit común."""
from datetime import datetime
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo

from petroandes.catalog.store import document_key, RevisionConflict
from petroandes.contracts.documents import Decision
from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path
from petroandes.index.common import file_digest
from .administration import ApprovalRequest, request_digest
from .models import DecisionRecord, Identity


def real_clock():
    return datetime.now(ZoneInfo("America/Bogota"))


def decision_id(request, document):
    return str(uuid5(NAMESPACE_URL, request_digest(request) + document_key(document) + document.pdf_sha256))


def make_record(request, spec, document, revision, reviewed):
    authority = "SIMULACIÓN ACADÉMICA: rol de " + spec.rol_area_simulado
    assumption = (f"Confirmación individual por el rol del área competente {spec.rol_area_simulado}, "
        f"supuesto académico expresamente autorizado por {request.revisor_humano}. "
        "No identifica ni acredita una autoridad real de PetroAndes. "
        "Autenticidad verificada únicamente dentro de esta simulación académica. "
        + " ".join(spec.restricciones))
    return DecisionRecord(decision=Decision(doc_id=document.doc_id,
        version_documental=document.version_documental, pdf_sha256=document.pdf_sha256,
        decision_id=decision_id(request, document), perfil="laboratorio", simulacion_academica=True,
        estado="certificado", evidencia=(f"app:{request.autorizacion.path}#sha256={request.autorizacion.sha256}",
                                        f"{document.pdf_uri}#sha256={document.pdf_sha256}"),
        autoridad=authority, revisor_humano=request.revisor_humano, revisado_en=reviewed,
        effective_from=reviewed, effective_to=request.effective_to, ambitos=(request.ambito,),
        usos=spec.usos, grupos=request.grupos, revision_gobierno=revision),
        supuesto=assumption, autenticidad="verificada")


def register(store, request, *, clock=real_clock):
    request = ApprovalRequest.model_validate_json(request.model_dump_json())
    if store.perfil != "laboratorio":
        raise ValueError("No se permite aplicar certificaciones a baseline")
    if file_digest(relative_path(request.autorizacion.path, APP_ROOT)) != request.autorizacion.sha256:
        raise ValueError("La evidencia de autorización cambió")
    store.db.execute("BEGIN IMMEDIATE")
    try:
        snapshot = store.snapshot()
        documents = {document_key(doc): doc for doc in snapshot.documentos}
        excluded = {(document_key(obs.documento), obs.pdf_sha256) for obs in snapshot.observaciones
                    if obs.estado == "excluido"}
        pairs, existing = [], []
        for spec in request.documentos:
            document = documents.get(document_key(Identity(doc_id=spec.doc_id,
                                                         version_documental=spec.version_documental)))
            if document is None or (document_key(document), document.pdf_sha256) in excluded:
                raise ValueError("Documento ausente o excluido; no se certifica")
            if not document.pdf_uri.startswith("project:"):
                raise ValueError("PDF sin raíz explícita")
            if file_digest(relative_path(document.pdf_uri[8:], PROJECT_ROOT)) != document.pdf_sha256:
                raise ValueError("PDF cambió; ninguna certificación se aplica")
            pairs.append((spec, document))
            row = store.db.execute("SELECT payload FROM decisions WHERE decision_id=?",
                                   (decision_id(request, document),)).fetchone()
            existing.append(DecisionRecord.model_validate_json(row[0]) if row else None)
        if any(existing):
            if not all(existing):
                raise ValueError("Lote previo incompleto; requiere investigación administrativa")
            for (spec, document), saved in zip(pairs, existing):
                if saved != make_record(request, spec, document, saved.decision.revision_gobierno,
                                        saved.decision.revisado_en):
                    raise ValueError("Decisión histórica no coincide; no sobrescribir")
            records, reused = existing, True
        else:
            if snapshot.revision != request.expected_revision:
                raise RevisionConflict("Gobierno cambió antes de incorporar el lote")
            reviewed = clock()
            if reviewed.tzinfo is None or reviewed.utcoffset() is None or reviewed >= request.effective_to:
                raise ValueError("Hora de revisión inválida o intervalo vencido")
            # Construir todos los modelos antes de escribir el primero.
            records = [make_record(request, spec, document, snapshot.revision + offset, reviewed)
                       for offset, (spec, document) in enumerate(pairs, 1)]
            for record in records:
                store.apply_decision(record, record.decision.revision_gobierno - 1)
            reused = False
        store.db.commit()
        return records, reused
    except Exception:
        store.db.rollback()
        raise
