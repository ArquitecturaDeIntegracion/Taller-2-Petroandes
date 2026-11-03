"""Audita bytes y legibilidad de los 19 PDF sin convertir Markdown en ingesta."""
import argparse
import hashlib
import json
from project_paths import PROJECT_ROOT

from f0_common import ROOT, write_report


def main():
    from pypdf import PdfReader

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    project = PROJECT_ROOT
    registry = json.loads((ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    pdf_root = (project / registry["corpus_pdf"]).resolve()
    md_root = (project / registry["corpus_md"]).resolve()
    if not pdf_root.is_relative_to(project) or not md_root.is_relative_to(project):
        raise ValueError("Corpus fuera de la raíz del taller")
    rows = []
    for path in sorted(pdf_root.rglob("*.pdf")):
        counterpart = md_root / path.relative_to(pdf_root).with_suffix(".md")
        if not path.resolve().is_relative_to(project) or not counterpart.resolve().is_relative_to(project):
            raise ValueError("Referencia externa al corpus")
        with path.open("rb") as source:
            reader = PdfReader(source, strict=True)
            if reader.is_encrypted or not reader.pages:
                raise ValueError(f"PDF no legible sin credenciales: {path.name}")
            pages = len(reader.pages)
        rows.append({"pdf": path.relative_to(project).as_posix(), "pages": pages,
                     "pdf_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "md_sha256": hashlib.sha256(counterpart.read_bytes()).hexdigest()})
    assert len(rows) == registry["expected_logical_documents"] == 19
    write_report(ROOT / args.output, {"status": "passed", "logical_documents": len(rows),
        "operation": "read_only_pdf_structure_and_hashes", "documents": rows,
        "content_equivalence_claimed": False, "governance_decisions_created": 0,
        "scope": "F0 legibilidad e inventario; extracción estructural corresponde a F3"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
