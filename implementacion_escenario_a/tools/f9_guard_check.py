"""Integra F9 original, fronteras MCP reales y cliente adversarial determinista."""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from project_paths import APP_ROOT
from f0_common import write_report
from record_command import record


def protected_inventory():
    roots = [APP_ROOT / "docs/revision", APP_ROOT / "evidence/revision/20261108-confirmada",
             APP_ROOT / "evidence/lab/20261103", APP_ROOT / "evidence/f9/20261108"]
    # La integridad del corpus también se valida por ingestión en F9 original.
    files = [APP_ROOT / "tools/f9_attack.py", APP_ROOT / "petroandes/compose/units.py",
             APP_ROOT / "config/mcp-demo.json", APP_ROOT / "knowledge/sources.json"]
    files.extend(path for root in roots if root.exists() for path in root.rglob("*") if path.is_file())
    inventory = {path.relative_to(APP_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in sorted(set(files))}
    return inventory


def invoke(script, destination, timeout):
    receipt, _, _ = record([sys.executable, str(APP_ROOT / "tools" / script),
                            "--output-dir", str(destination / "resultado")],
                           destination / "comando", timeout=timeout)
    path = destination / "resultado/summary.json"
    try:
        report = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, ValueError):
        report = {"status": "failed", "motivo": "Resumen ausente o ilegible"}
    return {"status": "passed" if receipt["exit_code"] == 0 and report.get("status") == "passed"
            else "failed", "exit_code": receipt["exit_code"], "summary": report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("El timeout debe ser positivo")
    destination = (APP_ROOT / args.output_dir).resolve()
    output_root = Path(os.environ.get("PETROANDES_F9_OUTPUT_DIR", APP_ROOT / "reports/portable")).resolve()
    if not destination.is_relative_to(output_root) or destination == output_root:
        parser.error("La salida debe estar dentro del directorio autorizado de reportes")
    destination.mkdir(parents=True, exist_ok=False)
    before = protected_inventory()
    write_report(destination / "integridad-antes.json", {"archivos": len(before),
                 "sha256_inventario": hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()}, emit=False)
    phases = {}
    for name, script in (("f9_original", "f9_attack.py"), ("fronteras_mcp", "f9_mcp_boundaries.py")):
        phases[name] = invoke(script, destination / name, args.timeout)
    try:
        from petroandes.security_lab import run_suite
        phases["frontera_consumidor"] = run_suite(destination / "frontera_consumidor")
    except Exception as exc:
        phases["frontera_consumidor"] = {"status": "failed", "tipo": type(exc).__name__, "motivo": str(exc)}
    intact = before == protected_inventory()
    summary = {"status": "passed" if intact and all(item.get("status") == "passed" for item in phases.values())
               else "failed", "version_arnes": "F9.1", "llm_real": "no_evaluado",
               "integridad_fuentes_y_reserva": intact,
               "reserva_ejecutada": False}
    # Cada fase conserva su propio resumen completo; el índice no duplica trazas.
    summary["fases"] = {name: {"status": result["status"],
                              "resumen": f"{name}/resultado/summary.json" if name != "frontera_consumidor"
                              else "frontera_consumidor/summary.json"} for name, result in phases.items()}
    write_report(destination / "summary.json", summary)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
