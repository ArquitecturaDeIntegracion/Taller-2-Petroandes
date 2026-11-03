"""Archivos de evidencia nuevos; JSONL en partes de 160 registros, sin sobrescritura."""
import json
from dataclasses import asdict
from pathlib import Path


def write_json(path, value):
    content = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if len(content.splitlines()) > 200:
        raise ValueError(f"Dividir informe de más de 200 líneas: {Path(path).name}")
    with Path(path).open("x", encoding="utf-8") as target:
        target.write(content)


def write_jsonl(folder, stem, records):
    names = []
    for index in range(0, len(records), 160):
        path = Path(folder) / f"{stem}-{index // 160 + 1:03d}.jsonl"
        with path.open("x", encoding="utf-8") as target:
            for record in records[index:index + 160]:
                target.write(json.dumps(record, ensure_ascii=False) + "\n")
        names.append(path.name)
    return names


def write_document(folder, report, sections=(), extraction=None):
    folder.mkdir(parents=True, exist_ok=False)
    write_json(folder / "report.json", report)
    if extraction:
        write_jsonl(folder, "sections", [asdict(section) for section in sections])
        for page, layout in enumerate(extraction["layout_pages"], 1):
            lines = layout.splitlines()
            for index in range(0, len(lines), 160):
                path = folder / f"layout-page-{page:03d}-part-{index // 160 + 1:03d}.txt"
                with path.open("x", encoding="utf-8") as target:
                    target.write("\n".join(lines[index:index + 160]) + "\n")
