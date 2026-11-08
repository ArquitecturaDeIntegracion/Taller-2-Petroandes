"""Extrae filas completas con cabecera y, para alarmas, el criterio literal."""
import re
from dataclasses import dataclass

from petroandes.contracts.documents import Fragment
from petroandes.retrieve.ranking import normalized_segment
from .intent import fold


@dataclass(frozen=True)
class Unit:
    source: Fragment
    text: str


def cells(line):
    return [fold(cell.strip()) for cell in line.split("|")]


def header(line, kind):
    cols = cells(line)
    if kind == "presion_activo":
        return cols == ["parametro", "valor de diseno", "limite de alarma"]
    if cols[0] != "tramo":
        return False
    if kind == "maop":
        return any(re.match(r"maop\b", col) for col in cols[1:])
    return any("umbral de alarma" in col for col in cols[1:]) and "ventana de evaluacion" in cols


def matches_row(line, kind, segment):
    value = line.split("|", 1)[0].strip()
    if kind == "presion_activo":
        return fold(value) == "presion de descarga"
    return fold(normalized_segment(value)) == segment


def table_units(parts, intent):
    rows, definitions = [], []
    for part in parts:
        for block in part.texto.split("\n\n"):
            lines = block.splitlines()
            current_header = None
            for line in lines:
                if header(line, intent.kind):
                    current_header = line
                elif "|" not in line:
                    current_header = None
                elif current_header and matches_row(line, intent.kind, intent.segment):
                    if len(cells(line)) == len(cells(current_header)) and any(char.isdigit() for char in line):
                        rows.append(Unit(part, current_header + "\n" + line))
            text = fold(block)
            if (intent.kind == "alarma_tramo" and "|" not in block
                    and "caida sostenida" in text and "por debajo del umbral" in text):
                definitions.append(Unit(part, block))
            if (intent.kind == "maop" and "|" not in block and "diseno" in text and "alarma" in text
                    and re.search(r"\bno\b", text)):
                definitions.append(Unit(part, block))
    if len(rows) != 1 or (intent.kind != "presion_activo" and not definitions):
        return ()
    return (*definitions, *rows)
