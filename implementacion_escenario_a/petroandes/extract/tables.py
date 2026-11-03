"""Reconstruye filas por columnas del layout PDF; falla ante alineación ambigua."""
import re

from .models import Block, ExtractionReview, Table


def cells(line):
    if re.match(r"^\s*[\x7f•]\s+", line.text):
        return ((len(line.text) - len(line.text.lstrip()), line.text.strip()),)
    return tuple((match.start(), match.group().strip()) for match in
                 re.finditer(r"\S+(?: \S+)*", line.text))


def read_table(lines, start):
    header_line = lines[start]
    header_cells = cells(header_line)
    if len(header_cells) < 2:
        raise ExtractionReview("Tabla sin columnas identificables")
    anchors, headers = zip(*header_cells)
    headers, header_lines = list(headers), [header_line]
    cursor = start + 1
    while cursor < len(lines) and lines[cursor].text.strip():
        pieces = cells(lines[cursor])
        columns = [min(range(len(anchors)), key=lambda i: abs(anchors[i] - p)) for p, _ in pieces]
        if not columns or 0 in columns:
            break
        for (position, text), column in zip(pieces, columns):
            if abs(anchors[column] - position) > 5:
                raise ExtractionReview("Cabecera multilínea ambigua")
            headers[column] += " " + text
        header_lines.append(lines[cursor])
        cursor += 1
    rows, traces, row, trace = [], [], [""] * len(headers), []

    def flush():
        nonlocal row, trace
        if trace:
            if not all(row):
                raise ExtractionReview("Fila con columnas vacías; requiere contraste visual")
            rows.append(tuple(row))
            traces.append(tuple(trace))
            row, trace = [""] * len(headers), []

    while cursor < len(lines):
        line = lines[cursor]
        if not line.text.strip():
            flush()
            cursor += 1
            continue
        pieces = cells(line)
        if not trace and len(pieces) < 2:
            break
        assigned = []
        for position, text in pieces:
            column = min(range(len(anchors)), key=lambda i: abs(anchors[i] - position))
            if abs(anchors[column] - position) > 5 or column in assigned:
                raise ExtractionReview("Alineación de tabla ambigua; no reasignar columnas")
            assigned.append(column)
            row[column] = " ".join(filter(None, (row[column], text)))
        trace.append(line)
        cursor += 1
    flush()
    if not rows:
        raise ExtractionReview("Tabla detectada sin filas completas")
    table = Table(tuple(headers), tuple(rows), tuple(traces), tuple(header_lines))
    text = "\n".join([" | ".join(headers), *[" | ".join(row) for row in rows]])
    used = (*header_lines, *(line for row in traces for line in row))
    return Block("tabla", text, used, table), cursor


def blocks(lines):
    result, paragraph = [], []

    def flush():
        if paragraph:
            text = " ".join(line.text.strip().replace("\x7f", "•") for line in paragraph)
            result.append(Block("prosa", text, tuple(paragraph)))
            paragraph.clear()

    cursor = 0
    while cursor < len(lines):
        line = lines[cursor]
        if not line.text.strip():
            flush()
            cursor += 1
        elif len(cells(line)) >= 2:
            flush()
            table, cursor = read_table(lines, cursor)
            result.append(table)
        else:
            paragraph.append(line)
            cursor += 1
    flush()
    return tuple(result)
