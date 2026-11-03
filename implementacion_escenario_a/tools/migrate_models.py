"""Reubica modelos materializados fuera de .venv, con comprobación de integridad."""
import argparse
import json
from pathlib import Path
from project_paths import APP_ROOT, MODELS_DIR
from f0_common import hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = (APP_ROOT / ".venv/model-files").resolve()
    destination = MODELS_DIR.resolve()
    if not source.is_relative_to(APP_ROOT) or not destination.is_relative_to(APP_ROOT):
        raise ValueError("La migración automática solo mueve modelos dentro de la implementación")
    if not source.is_dir():
        print("Sin modelos heredados para migrar")
        return 0
    if destination.exists():
        raise FileExistsError("El destino existe: no se sobreescriben modelos")
    before = hashes(source)
    if args.apply:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        if hashes(destination) != before:
            raise RuntimeError("No coincide la integridad tras mover modelos")
    print(json.dumps({"applied": args.apply, "source": ".venv/model-files",
                      "destination": destination.relative_to(APP_ROOT).as_posix(),
                      "verified_files": len(before)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
