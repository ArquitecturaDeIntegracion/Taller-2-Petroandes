"""Metadatos preliminares desde PDF; no es aún la partición estructural de F3."""
import hashlib
import re

from pypdf import PdfReader
from petroandes.contracts.documents import Document
from petroandes.paths import PROJECT_ROOT, relative_path

FAMILIES = {"01_manuales": "manual", "02_procedimientos": "procedimiento",
            "03_normativa": "resolucion", "04_actas": "acta",
            "05_comunicaciones": "comunicacion", "06_fichas": "ficha"}
HEADER = re.compile(r"Código\s+(.*?)\s+Versión\s+(.*?)\s+Fecha de emisión\s+(.*?)"
                    r"\s+Tipo\s+(.*?)\s+Área emisora\s+(.*?)\s+Activo / alcance", re.S)


def normalize(text):
    return " ".join(text.split())


def read_document(path):
    path = relative_path(path.relative_to(PROJECT_ROOT).as_posix(), PROJECT_ROOT)
    data = path.read_bytes()
    reader = PdfReader(path, strict=True)
    pages = tuple(page.extract_text() or "" for page in reader.pages)
    match = HEADER.search(pages[0])
    if not match:
        raise ValueError(f"Encabezado PDF no reconocido: {path.name}")
    code, version, issued, _declared_type, issuer = map(normalize, match.groups())
    prefix = [line.strip() for line in pages[0][:match.start()].splitlines() if line.strip()]
    if len(prefix) < 4:
        raise ValueError("Título PDF incompleto; requiere revisión")
    doc = Document(doc_id=code, version_documental=None if version == "—" else version,
        pdf_sha256=hashlib.sha256(data).hexdigest(), tipo=FAMILIES[path.parent.name],
        titulo=" ".join(prefix[3:]), emisor=issuer, fecha_emision=issued,
        pdf_uri="project:" + path.relative_to(PROJECT_ROOT).as_posix(), paginas=len(pages))
    return doc, pages
