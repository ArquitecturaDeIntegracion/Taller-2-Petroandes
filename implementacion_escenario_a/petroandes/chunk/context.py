"""Contexto explícito de prerrequisitos/condiciones; nunca una autorización."""
CONTEXT_POLICY = {"version": "conditions-es-1.0.0",
                  "secuencia": ["condiciones previas", "principio", "abortar"],
                  "recomendacion": ["alcance", "condiciones de aplicación"]}


def common_context(document, section, sections):
    titles = []
    if document.tipo == "procedimiento" and "secuencia" in section.title.casefold():
        titles = CONTEXT_POLICY["secuencia"]
    if document.tipo == "comunicacion" and ("recomend" in section.title.casefold()
                                              or section.section_id == "notas-de-la-version"):
        titles = CONTEXT_POLICY["recomendacion"]
    result = []
    for candidate in sections:
        if candidate != section and any(title in candidate.title.casefold() for title in titles):
            lines = [line for block in candidate.blocks for line in block.lines]
            result.append({"section_id": candidate.section_id, "title": candidate.title,
                "text": "\n\n".join(block.text for block in candidate.blocks),
                "pages": sorted({line.page for line in lines}),
                "source_lines": sorted({(line.page, line.number) for line in lines})})
    return result


def context_text(context):
    return "\n\n".join(f"Contexto [{item['title']}]:\n{item['text']}" for item in context)
