"""Prepara fragmentos trazables sin certificar documentos ni activar consultas."""
from datetime import datetime, timezone

from petroandes.chunk.structural import PARTITION, partition
from .contrast import compare_markdown
from .metadata import declared_scope, government_projection, observed_semantics
from .models import ExtractionReview
from .pdf import PARSER_VERSION, extract_pdf


def prepare_document(expected, path, markdown_path, snapshot, relations, tokenizer):
    document, sections, extraction = extract_pdf(path)
    if document != expected:
        raise ExtractionReview("Documento/hash del PDF distinto del catálogo; requiere registrar el cambio")
    contrast = compare_markdown(sections, markdown_path)
    scope = declared_scope(extraction["plain_pages"])
    fragments, parents = partition(document, sections, scope, tokenizer)
    government = government_projection(snapshot, document)
    semantics = observed_semantics(scope, sections)
    source_issuer = next(line.strip() for line in extraction["layout_pages"][0].splitlines() if line.strip())
    for record in fragments:
        fragment = record["fragment"]
        annex = fragment["section_id"].startswith("anexo-")
        record["metadata"] = {"documento": document.model_dump(mode="json"), "idioma": "es",
            "emisor_documental": source_issuer, "area_emisora": document.emisor,
            "formato_fuente": "pdf", "ingested_at": datetime.now(timezone.utc).isoformat(),
            "semantica_observada": semantics, "gobierno": government, "relaciones": relations,
            "tecnica": {"contrato_version": "corpus_documental_petroandes/1.0.0",
                "parser_version": PARSER_VERSION, "pypdf_version": extraction["pypdf_version"],
                "chunking_version": PARTITION, "embedding_bundle_id": tokenizer.config["bundle"],
                "tokenizer_revision": tokenizer.config["revision"], "index_revision": None},
            "seguridad": {"trust_level": "untrusted", "contenido_no_confiable": True,
                "security_flags": ["instrucciones_dirigidas_al_procesador"] if annex else [],
                "review_status": "contraste_lexico_ordenado_verificado"},
            "publication_state": "staging_no_autorizado"}
    report = {"doc_id": document.doc_id, "version_documental": document.version_documental,
        "pdf_sha256": document.pdf_sha256, "pdf_uri": document.pdf_uri, "tipo": document.tipo,
        "status": "preparado", "paginas": document.paginas, "secciones": len(sections),
        "fragmentos": len(fragments), "tablas": sum(bool(block.table) for sec in sections for block in sec.blocks),
        "filas": sum(len(block.table.rows) for sec in sections for block in sec.blocks if block.table),
        "max_tokens_entrada": max(record["fragment"]["tokens_entrada"] for record in fragments),
        "fuera_objetivo": sum(record["target_exception"] is not None for record in fragments),
        "contraste": contrast, "gobierno": government["estado"], "publicado": False}
    return report, fragments, parents, sections, extraction
