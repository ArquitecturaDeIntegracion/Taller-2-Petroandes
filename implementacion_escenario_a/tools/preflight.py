"""Inventario de lectura; no completa las pruebas de compatibilidad de F0."""
import hashlib
import importlib.metadata
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

from project_paths import APP_ROOT as ROOT, PROJECT_ROOT as PROJECT, portable
PACKAGES = ("pypdf", "pydantic", "qdrant-client", "sentence-transformers",
            "torch", "rank-bm25", "mcp", "laya", "pytest")


def node_inventory():
    executable = shutil.which("node")
    if not executable:
        return {"executable": None, "version": None, "inspector_minimum_met": False}
    try:
        result = subprocess.run([executable, "--version"], capture_output=True,
                                text=True, timeout=5, check=False)
        version = result.stdout.strip() if result.returncode == 0 else None
        match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", version or "")
        compatible = tuple(map(int, match.groups())) >= (22, 19, 0) if match else None
        return {"executable": executable, "version": version,
                "inspector_minimum_met": compatible}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"executable": executable, "version": None,
                "inspector_minimum_met": None, "error": str(exc)}


def main():
    registry = json.loads((ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    sources = []
    errors = []
    for item in registry["sources"]:
        path = (PROJECT / item["path"]).resolve()
        if not path.is_relative_to(PROJECT):
            errors.append(f"Fuente fuera del proyecto: {item['id']}")
            continue
        present = path.is_file()
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if present else None
        sources.append({"id": item["id"], "present": present,
                        "hash_matches": digest == item["sha256"]})
        if not present or digest != item["sha256"]:
            errors.append(f"Fuente ausente o modificada: {item['id']}")
    corpus = (PROJECT / registry["corpus_pdf"]).resolve()
    if not corpus.is_relative_to(PROJECT):
        raise ValueError("Corpus resuelto fuera del proyecto")
    files = sorted(corpus.rglob("*.pdf")) if corpus.is_dir() else []
    if any(not path.resolve().is_relative_to(PROJECT) for path in files):
        raise ValueError("Un enlace del corpus escapa del proyecto")
    expected = registry["expected_logical_documents"]
    if len(files) != expected:
        errors.append(f"Se esperaban {expected} PDF y se encontraron {len(files)}")
    markdown = (PROJECT / registry["corpus_md"]).resolve()
    if not markdown.is_relative_to(PROJECT):
        raise ValueError("Corpus Markdown resuelto fuera del proyecto")
    md_files = sorted(markdown.rglob("*.md")) if markdown.is_dir() else []
    if any(not path.resolve().is_relative_to(PROJECT) for path in md_files):
        raise ValueError("Un enlace Markdown escapa del proyecto")
    pdf_ids = [str(p.relative_to(corpus).with_suffix("")) for p in files]
    md_ids = [str(p.relative_to(markdown).with_suffix("")) for p in md_files]
    pairs_match = len(md_files) == expected and set(pdf_ids) == set(md_ids)
    if not pairs_match:
        errors.append("Las representaciones PDF y Markdown no coinciden por ruta y nombre")
    installed = {}
    for package in PACKAGES:
        try:
            installed[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed[package] = None
    node = node_inventory()
    warnings = []
    missing = [name for name, version in installed.items() if version is None]
    if missing:
        warnings.append("Dependencias de aplicación no detectadas: " + ", ".join(missing))
    if node["inspector_minimum_met"] is not True:
        warnings.append("Comprobar Node >= 22.19.0 antes de usar la versión actual de Inspector")
    report = {
        "operation": "read_only_inventory", "application_probes_executed": False,
        "phase_F0_complete": False, "implementation_root": str(ROOT),
        "project_root": str(PROJECT), "python": platform.python_version(),
        "python_executable": sys.executable, "platform": platform.platform(),
        "node": node, "packages": installed,
        "sources": sources, "corpus_pdf_count": len(files),
        "corpus_md_count": len(md_files), "representation_names_match": pairs_match,
        "corpus_files": [p.relative_to(PROJECT).as_posix() for p in files],
        "errors": errors, "warnings": warnings,
        "next_step": "Completar pruebas reales de F0; no inferir funcionamiento por instalación"
    }
    print(json.dumps(portable(report), ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
