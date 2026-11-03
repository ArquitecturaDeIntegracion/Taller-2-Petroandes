"""Secciones completas; solo dividir si exceden el máximo real de entrada E5."""
import hashlib
import json
from uuid import NAMESPACE_URL, uuid5

from petroandes.contracts.documents import Fragment
from petroandes.embeddings.input import passage_input
from petroandes.extract.models import ExtractionReview
from petroandes.extract.pdf import PARSER_VERSION
from .context import common_context, context_text

PARTITION = "structural-es-1.0.0"
TARGET = (250, 350)
MAX_TOKENS = 448
PROSE_OVERLAP_TOKENS = 0


def stable_uuid(values):
    return str(uuid5(NAMESPACE_URL, json.dumps(values, ensure_ascii=False, sort_keys=True)))


def section_text(section):
    return "\n\n".join(block.text for block in section.blocks)


def units(section):
    has_table = any(block.table for block in section.blocks)
    leading, result = [], []
    for block in section.blocks:
        if has_table and not result and not block.table:
            leading.append(block)
        elif block.table:
            for row, lines in zip(block.table.rows, block.table.row_lines):
                result.append((" | ".join(block.table.headers) + "\n" + " | ".join(row),
                               (*block.table.header_lines, *lines)))
        else:
            result.append((block.text, block.lines))
    return ("\n\n".join(block.text for block in leading),
            tuple(line for block in leading for line in block.lines), result)


def split_section(document, section, scope, tokenizer, context=""):
    full = section_text(section)
    all_lines = tuple(line for block in section.blocks for line in block.lines)
    if tokenizer.count(passage_input(document, section.title, scope, full, context)) <= MAX_TOKENS:
        return [(full, all_lines)]
    prefix, prefix_lines, atomic = units(section)
    groups, selected, selected_lines = [], [], []

    def text(items):
        return "\n\n".join(part for part in (prefix, *items) if part)

    for unit, lines in atomic:
        if tokenizer.count(passage_input(document, section.title, scope, text([unit]), context)) > MAX_TOKENS:
            raise ExtractionReview("Unidad estructural/condición excede 448 tokens; no cortarla")
        candidate = text([*selected, unit])
        if selected and tokenizer.count(passage_input(document, section.title, scope, candidate, context)) > TARGET[1]:
            groups.append((text(selected), (*prefix_lines, *selected_lines)))
            selected, selected_lines = [], []
        selected.append(unit)
        selected_lines.extend(lines)
    if selected:
        groups.append((text(selected), (*prefix_lines, *selected_lines)))
    if not groups:
        raise ExtractionReview("Sección excedida sin unidades divisibles")
    return groups


def partition(document, sections, scope, tokenizer):
    fragments, parents, order = [], [], 0
    for section in sections:
        context = common_context(document, section, sections)
        rendered_context = context_text(context)
        source_lines = [line for block in section.blocks for line in block.lines]
        parent_id = stable_uuid([document.doc_id, document.version_documental,
            str(document.fecha_emision), document.pdf_sha256, section.section_id,
            [(line.page, line.number) for line in source_lines], PARSER_VERSION, PARTITION])
        parent_id = stable_uuid([parent_id, rendered_context])
        child_ids = []
        for part, (text, lines) in enumerate(split_section(document, section, scope, tokenizer, rendered_context), 1):
            embedding_input = passage_input(document, section.title, scope, text, rendered_context)
            count = tokenizer.count(embedding_input)
            if count > MAX_TOKENS:
                raise ExtractionReview("Entrada completa E5 superior al máximo")
            chunk_id = stable_uuid([parent_id, part, hashlib.sha256(embedding_input.encode()).hexdigest(),
                                    tokenizer.config["bundle"]])
            fragment = Fragment(doc_id=document.doc_id, version_documental=document.version_documental,
                pdf_sha256=document.pdf_sha256, chunk_id=chunk_id, section_id=section.section_id,
                titulo_seccion=section.title, pagina_inicio=min(line.page for line in lines),
                pagina_fin=max(line.page for line in lines), parte=part, orden=order,
                parent_id=parent_id, texto=text, parser_version=PARSER_VERSION,
                particion=PARTITION, bundle=tokenizer.config["bundle"], tokens_entrada=count)
            fragments.append({"fragment": fragment.model_dump(mode="json"),
                "embedding_input": embedding_input,
                "embedding_input_sha256": hashlib.sha256(embedding_input.encode()).hexdigest(),
                "source_lines": sorted({(line.page, line.number) for line in lines}),
                "common_context": context,
                "target_exception": "seccion_breve" if count < TARGET[0] else
                                    "unidad_integra" if count > TARGET[1] else None})
            child_ids.append(chunk_id)
            order += 1
        parents.append({"parent_id": parent_id, "doc_id": document.doc_id,
            "version_documental": document.version_documental, "pdf_sha256": document.pdf_sha256,
            "section_id": section.section_id, "title": section.title, "text": section_text(section),
            "chunk_ids": child_ids, "page_start": min(line.page for line in source_lines),
            "page_end": max(line.page for line in source_lines), "contenido_no_confiable": True})
        parents[-1]["common_context"] = context
    return fragments, parents
