"""Inventario de entrega y comprobación de preparación académica."""
import json
from collections import Counter
from importlib.metadata import distributions
from pathlib import Path

from f0_common import write_report
from review_frozen import CONFIRMED, verify as verify_review
from petroandes.extract.output import write_jsonl
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT, INSPECTOR_DIR, PROJECT_ROOT, relative_path

APPLICATION_DIRS = (".agents", ".github", ".vscode", ".codex", "config", "contracts",
                    "docs", "knowledge", "petroandes", "tests", "tools")
APPLICATION_FILES = (".env.example", ".gitignore", ".mcp.json", "AGENTS.md", "INICIO.md",
                     "README.md", "compose.yaml", "config.json", "Dockerfile", "Dockerfile.dockerignore",
                     "pyproject.toml", "requirements.in", "requirements.lock",
                     "requirements-portable.lock", "requirements-dev.lock")
HISTORICAL_EVIDENCE = tuple(f"evidence/f{phase}" for phase in range(11)) + ("evidence/lab", "evidence/revision")
SOURCE_EXTRAS = ("ARTI4212_Caso_PetroAndes.pdf", ".gitattributes", ".gitignore",
                 "output/doc/Guia_Laboratorio_MCP_Inspector_PetroAndes.docx")
EXCLUDED = {".venv", "venv", ".cache", "__pycache__", ".pytest_cache", ".git", "node_modules"}
WEIGHTS = {".bin", ".onnx", ".safetensors", ".pt", ".pth", ".ckpt", ".npy", ".npz", ".gguf"}


def originals():
    source = json.loads((APP_ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    paths = [relative_path(entry["path"], PROJECT_ROOT) for entry in source["sources"]]
    paths += [path for path in (PROJECT_ROOT / "corpus").rglob("*") if path.is_file()]
    return {path.relative_to(PROJECT_ROOT).as_posix(): file_digest(path) for path in sorted(set(paths))}


def delivery_records():
    paths = {APP_ROOT / name for name in APPLICATION_FILES}
    for directory in (*APPLICATION_DIRS, *HISTORICAL_EVIDENCE):
        paths.update(path for path in (APP_ROOT / directory).rglob("*") if path.is_file())
    records = []
    for path in sorted(paths):
        ref = path.relative_to(APP_ROOT)
        if EXCLUDED.intersection(ref.parts):
            continue
        if ref.parts[0] == "evidence" and path.suffix in WEIGHTS:
            continue  # Las sondas generan los vectores de auditoría desde PDF.
        if not path.resolve().is_relative_to(APP_ROOT) or path.suffix in WEIGHTS:
            raise ValueError(f"Archivo fuera de la selección de entrega: {ref.as_posix()}")
        records.append({"base": "app", "path": ref.as_posix(), "sha256": file_digest(path)})
    sources = originals() | {name: file_digest(path) for name in SOURCE_EXTRAS
                             if (path := relative_path(name, PROJECT_ROOT)).is_file()}
    records.extend({"base": "project", "path": name, "sha256": sha} for name, sha in sources.items())
    return records


def delivery_files(destination):
    records = delivery_records()
    return {"archivos": len(records), "partes": write_jsonl(destination, "archivos", records)}


def python_licenses():
    rows = []
    for package in distributions():
        metadata = package.metadata
        text = (metadata.get("License") or "").strip()
        classifiers = [value for value in metadata.get_all("Classifier", []) if value.startswith("License ::")]
        files = sorted({str(path) for path in package.files or ()
                        if path.name.upper().startswith(("LICENSE", "COPYING", "NOTICE"))})
        rows.append({"nombre": metadata["Name"], "version": package.version,
                     "expresion": metadata.get("License-Expression"),
                     "licencia_declarada": text if len(text) <= 200 and "\n" not in text else None,
                     "texto_extenso_en_metadata": bool(text and (len(text) > 200 or "\n" in text)),
                     "clasificadores": classifiers, "archivos": files})
    return sorted(rows, key=lambda row: row["nombre"].casefold())


def node_licenses():
    lock = json.loads((INSPECTOR_DIR / "package-lock.json").read_text(encoding="utf-8"))
    rows = []
    for location in sorted(lock["packages"]):
        if not location:
            continue
        path = relative_path(location, INSPECTOR_DIR) / "package.json"
        if not path.is_file():
            continue  # paquetes opcionales de otra plataforma
        package = json.loads(path.read_text(encoding="utf-8"))
        rows.append({"nombre": package["name"], "version": package["version"],
                     "licencia_declarada": package.get("license"), "path": location})
    if not any(row["nombre"] == "@modelcontextprotocol/inspector" for row in rows):
        raise ValueError("El inventario npm no contiene MCP Inspector instalado")
    return rows


def license_inventory(destination):
    python, node = python_licenses(), node_licenses()
    return {"python": len(python), "npm": len(node),
            "python_sin_declaracion": [row["nombre"] for row in python if not any((
                row["expresion"], row["licencia_declarada"], row["texto_extenso_en_metadata"],
                row["clasificadores"], row["archivos"]))],
            "npm_sin_declaracion": sorted({row["nombre"] for row in node if not row["licencia_declarada"]}),
            "archivos": [*write_jsonl(destination, "licencias-python", python),
                         *write_jsonl(destination, "licencias-npm", node)]}


def academic_status(destination):
    if (CONFIRMED / "manifest.json").is_file():
        summary, cases = verify_review()
        rows = [{"id": case["case_id"], "particion": case["particion"],
                 "revision_humana": case["revision_humana"]["estado"],
                 "congelado": case["congelado_para_evaluacion"],
                 "sha256": file_digest(CONFIRMED / "casos" / f"{case['case_id']}.json")}
                for case in cases]
        return {"ejecutada": False, "casos_formales_ejecutados": 0, "minimo_reserva": 15,
                "casos_por_estado": {f"{part}/aprobada": count for part, count in summary["casos_congelados"].items()},
                "casos_congelados": len(rows), "sha256_manifiesto_congelado": summary["manifiesto_sha256"],
                "archivos": write_jsonl(destination, "casos-academicos", rows)}
    directory = APP_ROOT / "docs/revision"
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    states = Counter()
    inventory = []
    for name in manifest["case_refs"]:
        path = relative_path(name, directory)
        sha = file_digest(path)
        case = json.loads(path.read_text(encoding="utf-8"))
        status = case["revision_humana"]["estado"]
        states[case["particion_propuesta"], status] += 1
        inventory.append({"id": case["case_id"], "particion": case["particion_propuesta"],
                          "revision_humana": status, "congelado": case["congelado_para_evaluacion"],
                          "sha256": sha, "coincide_manifiesto_propuestas": sha == manifest["sha256_fichas_propuestas"][name]})
    return {"ejecutada": False, "casos_formales_ejecutados": 0, "minimo_reserva": 15,
            "casos_por_estado": {f"{part}/{state}": count for (part, state), count in sorted(states.items())},
            "propuestas_congeladas": sum(row["congelado"] is True for row in inventory),
            "sha256_manifiesto_propuestas": file_digest(manifest_path),
            "archivos": write_jsonl(destination, "casos-academicos", inventory)}


def inventory(destination):
    destination.mkdir()
    summary = {"archivos_entrega": delivery_files(destination), "dependencias": license_inventory(destination),
               "evaluacion_formal": academic_status(destination)}
    write_report(destination / "summary.json", summary, emit=False)
    return summary
