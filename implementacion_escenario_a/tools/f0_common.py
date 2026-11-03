"""Utilidades de evidencia para sondas reales, sin modificar los originales."""
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from project_paths import APP_ROOT as ROOT, CACHE_DIR, portable
CACHE = CACHE_DIR / "huggingface"


def configure_cache(offline=False):
    os.environ["HF_HOME"] = str(CACHE)
    os.environ["HF_HUB_CACHE"] = str(CACHE / "hub")
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"


def memory():
    import psutil
    process = psutil.Process()
    return {"process_rss_bytes": process.memory_info().rss,
            "process_peak_wset_bytes": getattr(process.memory_info(), "peak_wset", None),
            "system_total_bytes": psutil.virtual_memory().total,
            "system_available_bytes": psutil.virtual_memory().available}


def versions():
    names = ("pypdf", "pydantic", "qdrant-client", "sentence-transformers", "torch",
             "transformers", "rank-bm25", "mcp", "laya", "pytest", "psutil")
    result = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def hashes(directory):
    result = {}
    for path in sorted(Path(directory).rglob("*")):
        if not path.is_file() or ".cache" in path.relative_to(directory).parts:
            continue
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        result[path.relative_to(directory).as_posix()] = digest.hexdigest()
    return result


def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {"recorded_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "executable": sys.executable,
              "command": [sys.executable, *sys.argv], **report}
    report = {"evidence_schema_version": 2, "path_encoding": "portable-placeholders", **portable(report)}
    content = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if len(content.splitlines()) > 200:
        raise ValueError("Dividir evidencia: el informe supera 200 líneas")
    if path.exists():
        raise FileExistsError(f"No sobrescribir evidencia: {path}")
    path.write_text(content, encoding="utf-8")
    print(content, end="")
