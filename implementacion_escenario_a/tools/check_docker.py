"""Valida la imagen construida y conserva evidencia real sin reinicializar Docker."""
import argparse
import json
import os
import sys

from project_paths import APP_ROOT, MODELS_DIR
from f0_common import write_report
from record_command import record


SEED = """
import json
import shutil
from pathlib import Path
from f0_common import hashes
source, destination = Path('/seed/models'), Path('.cache/models')
destination.mkdir(parents=True, exist_ok=True)
copied = []
for model in source.iterdir():
    if not model.is_dir() or model.name.startswith('.'):
        continue
    target = destination / model.name
    if not target.exists():
        shutil.copytree(model, target)
        copied.append(model.name)
    if hashes(model) != hashes(target):
        raise RuntimeError('El modelo existente difiere: ' + model.name)
print(json.dumps({'copied': copied, 'hashes_match': True}))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seed-host-models", action="store_true",
        help="Copia modelos locales al volumen Docker sin sobrescribir y compara hashes")
    args = parser.parse_args()
    os.chdir(APP_ROOT)
    destination = APP_ROOT / args.output_dir
    destination.mkdir(parents=True, exist_ok=False)
    results = []
    seeded = False

    def run(name, command):
        report, stdout, stderr = record(command, destination / name)
        results.append({"check": name, "exit_code": report["exit_code"],
                        "seconds": round(report["elapsed_seconds"], 2)})
        print(f"{name}: exit={report['exit_code']}", flush=True)
        if report["exit_code"]:
            print(stdout[-3000:] + stderr[-3000:], file=sys.stderr, flush=True)
            raise RuntimeError(f"Falló {name}; consultar sus logs")
        return stdout

    compose = ["docker", "compose"]
    container = compose + ["run", "--rm", "--no-deps", "project"]
    try:
        run("engine", ["docker", "version"])
        run("compose", compose + ["config", "--quiet"])
        run("image", ["docker", "image", "inspect", "petroandes-educativo:local",
                      "--format", "{{json .Id}} {{json .RepoTags}}"])
        run("pip-check", container + ["-m", "pip", "check"])
        run("freeze-linux", container + ["-m", "pip", "freeze", "--all"])
        run("environment", container + ["tools/f0.py", "environment", "--output",
            f"{args.output_dir}/environment.json"])
        run("preflight", container + ["tools/preflight.py"])
        run("validate-agent", container + ["tools/validate_agent.py"])
        run("tests", container + ["-m", "pytest", "-q", "-p", "no:cacheprovider",
                                "--basetemp", "artifacts/pytest-docker-validation"])
        dev = compose + ["--profile", "dev", "run", "--rm", "--no-deps", "dev"]
        run("dev-preflight", dev + ["tools/preflight.py"])
        run("dev-tests", dev + ["-m", "pytest", "-q", "-p", "no:cacheprovider",
                               "--basetemp", "artifacts/pytest-dev-validation"])
        run("storage", container + ["tools/f0.py", "storage", "--output",
                                    f"{args.output_dir}/storage.json"])
        run("corpus", container + ["tools/f0_corpus.py", "--output",
                                   f"{args.output_dir}/corpus.json"])
        run("mcp", container + ["tools/f0_mcp.py", "--output-dir",
                                f"{args.output_dir}/mcp-transcript"])
        run("debug", container + ["tools/debug_smoke.py", "--output",
                                  f"{args.output_dir}/debug.json"])
        if args.seed_host_models:
            if not MODELS_DIR.is_dir():
                raise FileNotFoundError("No existen modelos locales para copiar")
            seed_command = compose + ["run", "--rm", "--no-deps", "--volume",
                f"{MODELS_DIR}:/seed/models:ro", "project", "-c",
                "import sys; sys.path.insert(0, 'tools');\n" + SEED]
            run("seed-models", seed_command)
            seeded = True
        for model in ("e5", "laya"):
            run(model, container + ["tools/f0.py", model, "--offline", "--output",
                                   f"{args.output_dir}/{model}.json"])
        run("closure", container + ["tools/check_f0.py", "--output",
                                    f"{args.output_dir}/closure.json"])
        status, error = "passed", None
    except Exception as exc:
        status, error = "failed", str(exc)
    write_report(destination / "summary.json", {"status": status, "checks": results,
        "error": error, "models_seeded_from_host": seeded,
        "scope": "Imagen Linux y sondas reales; no acredita revisión académica ni UI VS Code",
        "application_complete": False, "academic_approvals_created": 0})
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
