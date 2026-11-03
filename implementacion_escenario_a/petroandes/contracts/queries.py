"""Entradas públicas MCP: sin identidad, perfil ni privilegios autoasignados."""
from typing import Annotated

from pydantic import Field, StringConstraints

from .common import Contract, DocumentType, Sha256, Text

QueryText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True,
                                           min_length=1, max_length=2000)]


class SearchFilters(Contract):
    tipo: DocumentType | None = None
    activo: Text | None = None
    tramo: Text | None = None


class SearchQuery(Contract):
    consulta: QueryText
    top_k: int = Field(default=5, strict=True, ge=1, le=10)
    filtros: SearchFilters | None = None


class FragmentQuery(Contract):
    doc_id: Text
    version_documental: Text | None
    section_id: Text
    parte: int | None = Field(default=None, strict=True, ge=1)
    pdf_sha256: Sha256 | None = None
