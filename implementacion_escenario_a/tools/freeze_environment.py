"""Congela las distribuciones observadas y comprueba requisitos instalados."""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from project_paths import INSPECTOR_DIR
from f0_common import ROOT, write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if sys.prefix == sys.base_prefix:
        raise RuntimeError("Ejecutar exclusivamente dentro del entorno aislado")
    check = subprocess.run([sys.executable, "-m", "pip", "check"],
                           capture_output=True, text=True, check=True)
    result = subprocess.run([sys.executable, "-m", "pip", "freeze", "--all"],
                            capture_output=True, text=True, check=True)
    lines = sorted(line for line in result.stdout.splitlines() if line)
    if len(lines) > 199 or any("==" not in line for line in lines):
        raise ValueError("El bloqueo requiere versiones exactas y máximo 200 líneas")
    lock = ROOT / "requirements.lock"
    if lock.exists():
        raise FileExistsError("No sobrescribir un bloqueo ya conservado")
    lock.write_text("\n".join(lines) + "\n", encoding="utf-8")
    inspector = INSPECTOR_DIR
    archive = ROOT / "evidence" / "f0" / "inspector-lock.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "x", ZIP_DEFLATED) as bundle:
        for name in ("package.json", "pnpm-lock.yaml"):
            bundle.write(inspector / name, arcname=name)
    write_report(ROOT / args.output, {"status": "passed", "pip_check": check.stdout.strip(),
        "python_lock": str(lock.relative_to(ROOT)), "distributions": len(lines),
        "python_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "inspector_lock": str(archive.relative_to(ROOT)),
        "inspector_lock_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "python_lock_mechanism": "pip freeze --all; instalar con pip -r requirements.lock",
        "inspector_lock_mechanism": "pnpm 11.25.0; herramienta Node independiente"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
