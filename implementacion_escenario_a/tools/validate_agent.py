"""Valida estructura, límites y referencias del paquete con biblioteca estándar."""
import ast
import hashlib
import json
import os
import re
import sys
import tomllib
from pathlib import Path

from project_paths import APP_ROOT as ROOT, PROJECT_ROOT as PROJECT
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".cache", "artifacts", "models"}


def project_files():
    for directory, children, files in os.walk(ROOT, followlinks=False):
        children[:] = sorted(name for name in children if name not in SKIP)
        for name in sorted(files):
            yield Path(directory) / name


def main():
    errors = []
    counts = []
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    limit = config["limits"]["max_lines_per_text_file"]
    if limit != 200:
        errors.append("El límite requerido es exactamente 200 líneas")
    for path in project_files():
        relative = path.relative_to(ROOT)
        if not path.is_file() or any(part in SKIP for part in relative.parts):
            continue
        if not path.resolve().is_relative_to(ROOT):
            errors.append(f"Enlace fuera del paquete: {relative}")
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        count = len(text.splitlines())
        counts.append((count, str(relative)))
        if count > limit:
            errors.append(f"{relative}: {count} líneas supera {limit}")
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix == ".toml":
            tomllib.loads(text)
        if path.suffix == ".py":
            ast.parse(text, filename=str(relative))
        if path.suffix == ".md":
            if len(re.findall(r"^```", text, re.M)) % 2:
                errors.append(f"Bloque de código sin cerrar: {relative}")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                destination = (path.parent / target.split("#")[0].strip("<>")).resolve()
                if not destination.is_relative_to(PROJECT) or not destination.exists():
                    errors.append(f"Referencia inválida: {relative} -> {target}")
    for field in ("instructions", "startup_prompt", "native_config", "knowledge_index",
                  "source_registry", "state_file"):
        destination = (ROOT / config[field]).resolve()
        if not destination.is_relative_to(ROOT) or not destination.is_file():
            errors.append(f"Falta referencia de config.json: {field}")
    native = tomllib.loads((ROOT / config["native_config"]).read_text(encoding="utf-8"))
    if native.get("model_reasoning_effort") != config["model"]["reasoning_effort_default"]:
        errors.append("El manifiesto y el TOML difieren en esfuerzo predeterminado")
    for name in config["skills"]:
        path = ROOT / config["skills_root"] / name / "SKILL.md"
        if not path.is_file():
            errors.append(f"Habilidad ausente: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not match or f"name: {name}\n" not in match[1] + "\n":
            errors.append(f"Nombre/frontmatter inválido: {name}")
        elif not re.search(r"^description: .+", match[1], re.M):
            errors.append(f"Descripción ausente: {name}")
    registry = json.loads((ROOT / config["source_registry"]).read_text(encoding="utf-8"))
    for source in registry["sources"]:
        path = (PROJECT / source["path"]).resolve()
        if not path.is_relative_to(PROJECT) or not path.is_file():
            errors.append(f"Fuente inválida: {source['id']}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            errors.append(f"Fuente modificada desde el registro: {source['id']}")
    for count, name in counts:
        print(f"{count:3d} líneas  {name}")
    if errors:
        print("\nERRORES:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print(f"\nOK: {len(counts)} archivos textuales; máximo {max(n for n, _ in counts)} líneas.")
    print("Estructura validada; no comprueba una sesión real de VS Code ni termina F0.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, SyntaxError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
