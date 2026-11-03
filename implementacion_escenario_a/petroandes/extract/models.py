"""Estructuras internas con páginas y líneas de la extracción PDF preservadas."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    page: int
    number: int
    text: str


@dataclass(frozen=True)
class Table:
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    row_lines: tuple[tuple[Line, ...], ...]
    header_lines: tuple[Line, ...]


@dataclass(frozen=True)
class Block:
    kind: str
    text: str
    lines: tuple[Line, ...]
    table: Table | None = None


@dataclass(frozen=True)
class Section:
    section_id: str
    title: str
    blocks: tuple[Block, ...]


class ExtractionReview(ValueError):
    """Defecto o ambigüedad: conservar para revisión, sin publicar fragmentos."""
