"""Contraste lexical ordenado; Markdown nunca construye ni corrige fragmentos."""
import difflib
import hashlib
import re
import unicodedata

from .models import ExtractionReview


def lexical_tokens(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.findall(r"[^\W_]+(?:[.,]\d+)*|[±%°/]|[−-](?=\d)", text, re.UNICODE)


def pdf_body(sections):
    return "\n".join(section.title + "\n" + "\n".join(block.text for block in section.blocks)
                     for section in sections)


def compare_markdown(sections, markdown_path):
    data = markdown_path.read_bytes()
    markdown = data.decode("utf-8-sig")
    body = re.search(r"^##\s+", markdown, re.M)
    if not body:
        raise ExtractionReview("Markdown de contraste sin cuerpo identificable")
    expected_headings = [lexical_tokens(title) for title in re.findall(r"^##\s+(.+)$", markdown, re.M)]
    actual_headings = [lexical_tokens(section.title) for section in sections]
    if expected_headings != actual_headings:
        raise ExtractionReview("Secciones PDF/Markdown distintas; revisar reglas del parser PDF")
    expected, actual = lexical_tokens(markdown[body.start():]), lexical_tokens(pdf_body(sections))
    if expected != actual:
        matcher = difflib.SequenceMatcher(a=expected, b=actual, autojunk=False)
        differences = [{"operation": tag, "md": expected[i:j], "pdf": actual[k:l]}
                       for tag, i, j, k, l in matcher.get_opcodes() if tag != "equal"]
        raise ExtractionReview("Diferencia PDF/Markdown: " + repr(differences[:3]))
    return {"status": "coincide_lexico_ordenado", "tokens_contrastados": len(actual),
            "md_sha256": hashlib.sha256(data).hexdigest(), "markdown_usado_como_ingesta": False}
