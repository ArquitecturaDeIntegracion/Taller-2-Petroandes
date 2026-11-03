"""Layout pypdf versionado: secciones, artículos y anexos con procedencia por página."""
import importlib.metadata
import re
import unicodedata

from pypdf import PdfReader
from petroandes.governance.pdf_metadata import read_document
from .models import ExtractionReview, Line, Section
from .tables import blocks

PARSER_VERSION = "pypdf-layout-es-1.0.1"
COMMUNICATION_HEADINGS = {"Asunto", "Antecedente", "Recomendación", "Alcance", "Recomendación técnica", "Contenido de la versión",
    "Condiciones de aplicación", "Notas de la versión", "Anexo — notas de integración"}


def slug(value):
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.casefold()).strip("-")


def heading(text, family):
    text = text.strip()
    number = re.fullmatch(r"(\d+)\.\s+(.+)", text)
    article = re.fullmatch(r"Artículo (\d+)\.\s+(.+)", text)
    if article:
        return f"articulo-{article[1]}", text
    if number:
        return number[1], text
    if family == "comunicacion" and text in COMMUNICATION_HEADINGS:
        return slug(text), text
    if family == "resolucion" and text == "Considerando":
        return "considerando", text
    return None


def sections_from_layout(pages, family):
    sections, title, key, lines = [], None, None, []
    for page_number, layout in enumerate(pages, 1):
        for line_number, text in enumerate(layout.splitlines(), 1):
            if text.strip().startswith("Documento sintético de uso académico"):
                break  # pie de página físico: no es contenido de la sección
            if re.fullmatch(r"Página\s+\d+", text.strip()):
                continue
            found = heading(text, family)
            if found:
                if title is not None:
                    sections.append(Section(key, title, blocks(lines)))
                key, title = found
                lines = []
            elif title is not None:
                lines.append(Line(page_number, line_number, text))
    if title is not None:
        sections.append(Section(key, title, blocks(lines)))
    if not sections or any(not section.blocks for section in sections):
        raise ExtractionReview("Secciones ausentes o vacías")
    if len({section.section_id for section in sections}) != len(sections):
        raise ExtractionReview("Identificador de sección repetido")
    return tuple(sections)


def extract_pdf(path):
    document, plain_pages = read_document(path)
    reader = PdfReader(path, strict=True)
    layouts = tuple(page.extract_text(extraction_mode="layout") or "" for page in reader.pages)
    if any(not text.strip() for text in layouts):
        raise ExtractionReview("Página sin texto extraíble; no sustituir por Markdown")
    sections = sections_from_layout(layouts, document.tipo)
    return document, sections, {"parser_version": PARSER_VERSION,
        "pypdf_version": importlib.metadata.version("pypdf"), "plain_pages": plain_pages,
        "layout_pages": layouts, "normalizations": ["unir saltos visuales dentro de celda/párrafo",
        "DEL de viñeta PDF representado como •", "retirar metadatos iniciales y pie físico"]}
