"""Selección directa y contexto trazable a fragmentos autorizados."""
from petroandes.contracts.responses import Citation
from petroandes.index.publication import document_identity


def citation(fragment):
    return Citation(**fragment.model_dump(include={
        "doc_id", "version_documental", "pdf_sha256", "section_id", "pagina_inicio", "pagina_fin",
    })).model_dump(mode="json")


def direct_parts(query, records):
    documents = [part for part, _ in records.values()
                 if part.doc_id == query.doc_id and part.version_documental == query.version_documental
                 and (query.pdf_sha256 is None or part.pdf_sha256 == query.pdf_sha256)]
    if len({part.pdf_sha256 for part in documents}) > 1:
        return None
    return sorted((part for part in documents if part.section_id == query.section_id
                   and (query.parte is None or query.parte == part.parte)), key=lambda part: part.orden)


def context_parts(chunk_id, records):
    match = records.get(chunk_id)
    if match is None:
        return []
    anchor, record = match
    identity = document_identity(anchor)
    sections = {item["section_id"] for item in record.get("common_context", ())}
    return sorted(
        (part for part, _ in records.values() if document_identity(part) == identity
         and (part.chunk_id == chunk_id or (anchor.parent_id and part.parent_id == anchor.parent_id
                                            and part.section_id == anchor.section_id)
              or part.section_id in sections)),
        key=lambda part: part.orden,
    )
