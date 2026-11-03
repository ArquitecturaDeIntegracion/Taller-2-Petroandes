"""Clasificación inicial acordada: evidencia PDF, nunca certificaciones positivas."""
import hashlib
import json
import re

from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path
from .models import Identity, Observation, PdfEvidence, Relation
from .pdf_metadata import normalize, read_document

EXCLUSIONS = {
    ("PRO-MED-007", "1"): (("PRO-MED-007", "2"), "encabezado",
        "Reemplaza a PRO-MED-007 v1"),
    ("PRO-OPE-012", "2"): (("PRO-OPE-012", "3"), "3.1",
        "Los umbrales y las ventanas de esta versión reemplazan íntegramente los de la versión anterior."),
    ("PRO-SEG-009", "1"): (("PRO-SEG-015", "1"), "1",
        "Este procedimiento reemplaza íntegramente el PRO-SEG-009 v1"),
    ("RES-CREG-0112-2021", None): (("RES-CREG-0043-2024", None), "articulo-6",
        "La presente resolución rige a partir de su publicación y deroga en su integridad la Resolución 0112 de 2021."),
}


def identity(doc):
    return Identity(doc_id=doc.doc_id, version_documental=doc.version_documental)


def evidence(doc, pages, section, quote):
    found = [index + 1 for index, text in enumerate(pages) if quote in normalize(text)]
    if len(found) != 1:
        raise ValueError(f"Cláusula PDF ausente o ambigua: {doc.doc_id}/{section}")
    return PdfEvidence(fuente=identity(doc), pdf_sha256=doc.pdf_sha256,
                       section_id=section, pagina=found[0], cita=quote)


def load_baseline():
    registry = json.loads((APP_ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    corpus = relative_path(registry["corpus_pdf"], PROJECT_ROOT)
    records = [read_document(path) for path in sorted(corpus.rglob("*.pdf"))]
    if len(records) != registry["expected_logical_documents"] or len(records) != 19:
        raise ValueError("El corpus inicial requiere 19 PDF")
    by_id = {(doc.doc_id, doc.version_documental): (doc, pages) for doc, pages in records}
    if len(by_id) != 19:
        raise ValueError("Identidades documentales duplicadas")
    observations, relations = [], []
    for doc, pages in records:
        key = (doc.doc_id, doc.version_documental)
        sources = ()
        if key in EXCLUSIONS:
            source_key, section, quote = EXCLUSIONS[key]
            source, source_pages = by_id[source_key]
            sources = (evidence(source, source_pages, section, quote),)
        state = "excluido" if sources else "pendiente"
        reason = ("Sustitución o derogación expresa: " + sources[0].cita if sources else
                  "Falta certificación del área; no inferir vigencia ni identificar el manual retirado.")
        oid = hashlib.sha256((doc.pdf_sha256 + state).encode()).hexdigest()
        observations.append(Observation(observation_id=oid, documento=identity(doc),
            pdf_sha256=doc.pdf_sha256, estado=state, fundamento=reason, fuentes=sources))
        replacement = re.search(r"Reemplaza a\s+([A-Z][A-Z0-9-]+)\s+v(\d+)", pages[0])
        if replacement:
            old_code, old_version = replacement.groups()
            quote = f"Reemplaza a {old_code} v{old_version}"
            relations.append(Relation(relation_id="reemplaza:" + oid, tipo="reemplaza",
                desde=identity(doc), hacia=Identity(doc_id=old_code, version_documental=old_version),
                evidencia=evidence(doc, pages, "encabezado", quote)))
    source, pages = by_id[("RES-CREG-0043-2024", None)]
    _, section, quote = EXCLUSIONS[("RES-CREG-0112-2021", None)]
    relations.append(Relation(relation_id="deroga:" + source.pdf_sha256, tipo="deroga",
        desde=identity(source), hacia=Identity(doc_id="RES-CREG-0112-2021", version_documental=None),
        evidencia=evidence(source, pages, section, quote)))
    if sum(item.estado == "excluido" for item in observations) != 4:
        raise ValueError("Clasificación inicial inconsistente")
    return tuple(doc for doc, _ in records), tuple(observations), tuple(relations)
