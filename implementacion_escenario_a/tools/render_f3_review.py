"""Renderiza copias de lectura de los PDF del corpus y conserva comandos y hashes."""
import argparse
import hashlib
import json
import shutil

from pypdf import PdfReader
from project_paths import APP_ROOT, PROJECT_ROOT
from f0_common import write_report
from record_command import record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    folder = APP_ROOT / args.output_dir
    folder.mkdir(parents=True, exist_ok=False)
    renderer = shutil.which("pdftoppm")
    if not renderer:
        raise RuntimeError("Poppler pdftoppm no disponible para revisión visual")
    registry = json.loads((APP_ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    files = sorted((PROJECT_ROOT / registry["corpus_pdf"]).rglob("*.pdf"))
    renderings = []
    for index, path in enumerate(files, 1):
        if len(PdfReader(path).pages) != 1:
            raise ValueError("Extender revisión visual a todas las páginas del PDF multipágina")
        prefix = folder / path.stem
        result, _, stderr = record([renderer, "-singlefile", "-r", "105", "-png", str(path), str(prefix)],
                                   folder / f"command-{index:02d}", timeout=60)
        if result["exit_code"] != 0:
            raise RuntimeError(f"No se pudo renderizar {path.name}")
        png = prefix.with_suffix(".png")
        renderings.append({"pdf": path.relative_to(PROJECT_ROOT).as_posix(),
            "pdf_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "png": png.name, "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
            "renderer_warning_lines": len(stderr.splitlines())})
    write_report(folder / "render-manifest.json", {"operation": "read_only_pdf_render",
        "pages": len(renderings), "dpi": 105, "renderings": renderings,
        "visual_inspection_required": True, "source_pdfs_modified": False})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
