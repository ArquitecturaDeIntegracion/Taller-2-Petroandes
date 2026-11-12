"""Reproduce en serie la entrega técnica, con artefactos nuevos y evidencia por etapa."""
import argparse
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from f0_common import write_report
from f11_inventory import inventory, originals
from project_paths import APP_ROOT
from record_command import record


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class Validation:
    def __init__(self, destination, artifacts):
        self.destination = destination
        self.environment = {**os.environ, "PETROANDES_ARTIFACTS_DIR": str(artifacts),
                            "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        self.steps = {}

    def run(self, label, *command):
        print(f"F11 · {label}", flush=True)
        receipt, stdout, _ = record([sys.executable, *map(str, command)],
                                     self.destination / "comandos" / label, env=self.environment)
        self.steps[label] = {"exit_code": receipt["exit_code"], "segundos": receipt["elapsed_seconds"],
                             "recibo": f"comandos/{label}/command.json"}
        require(receipt["exit_code"] == 0, f"Falló {label}; consulta su recibo y salida")
        return stdout

    def script(self, label, name, *arguments):
        return self.run(label, APP_ROOT / "tools" / name, *arguments)

    def probes(self):
        self.run("dependencias", "-m", "pip", "check")
        self.script("estructura", "validate_agent.py")
        preflight = json.loads(self.script("preflight", "preflight.py"))
        require(not preflight["errors"] and preflight["corpus_pdf_count"] == preflight["corpus_md_count"] == 19,
                "El inventario debe contener 19 PDF y 19 Markdown sin errores")
        require(all(source["hash_matches"] for source in preflight["sources"]),
                "Una fuente del taller difiere del registro de procedencia")
        for model in ("e5", "laya"):
            result_path = self.destination / "modelos" / f"{model}.json"
            self.script(f"modelo-{model}", "f0.py", model, "--offline", "--output", result_path)
            require(load(result_path)["status"] == "passed", f"El modelo {model} no pasó su sonda")
        return {"pdf": preflight["corpus_pdf_count"], "markdown": preflight["corpus_md_count"],
                "fuentes_verificadas": len(preflight["sources"])}

    def rebuild(self, workspace):
        profile = ("--profile", "baseline")
        self.run("catalogo-baseline", "-m", "petroandes.catalog", "init", *profile,
                 "--evidence-dir", workspace / "catalogo")
        catalog = load(workspace / "catalogo/summary.json")
        require(catalog["governance_revision"] == 1 and
                catalog["clasificacion"] == {"certificado": 0, "excluido": 4, "pendiente": 15},
                "El catálogo inicial perdió pendientes o exclusiones")
        staging = workspace / "staging"
        self.run("ingesta-pdf", "-m", "petroandes.extract", *profile, "--output-dir", staging)
        extracted = load(staging / "manifest.json")
        require(extracted["preparados"] == 19 and extracted["fragmentos"] == 92 and not extracted["rechazados"],
                "La ingesta inicial debe extraer 92 fragmentos de los 19 PDF")
        out = self.destination / "baseline"
        self.script("consolidacion-baseline", "f10.py", *profile, "--output-dir", out,
                    "consolidar", "--stage", staging / "manifest.json")
        published = load(out / "summary.json")
        require(published["status"] == "passed" and published["publicacion"]["published_fragments"] == 0
                and published["eventos_confirmados"] == 1, "El baseline publicó evidencia sin aprobación")
        status = json.loads(self.run("estado-baseline", "-m", "petroandes.catalog", "status", *profile))
        require(status["eventos_pendientes"] == 0, "El evento inicial del baseline sigue pendiente")
        response = json.loads(self.script("consulta-baseline", "f5.py", *profile, "responder",
                                          "--consulta", "Presión de descarga de P-101", "--top-k", "5"))["resultado"]
        direct = json.loads(self.script("directa-excluida", "f5.py", *profile, "obtener",
                                        "--doc-id", "PRO-MED-007", "--version", "1", "--seccion", "3"))["resultado"]
        require(response["estado"] == "abstencion" and response["motivo_abstencion"] == "sin_evidencia_autorizada",
                "La consulta baseline no devolvió la abstención esperada")
        require(direct["estado"] == "denegado" and direct["error"] == "evidencia_no_autorizada",
                "La obtención directa de la versión excluida no fue denegada")
        report = {"revision": 1, "clasificacion": catalog["clasificacion"], "fragmentos_extraidos": 92,
                  "fragmentos_publicados": 0, "eventos_pendientes": status["eventos_pendientes"],
                  "consulta": response["estado"], "directa_excluida": direct["estado"]}
        write_report(out / "reconstruccion.json", report, emit=False)
        return report

    def critical_controls(self):
        self.run("regresion", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                 "-c", APP_ROOT / "pyproject.toml", APP_ROOT / "tests")
        tools = {"f7": "f7_inspector.py", "f8": "f8_evaluate.py", "f9": "f9_attack.py", "f10": "f10_check.py"}
        reports = {}
        for phase, script in tools.items():
            output = self.destination / phase
            self.script(phase, script, "--output-dir", output)
            reports[phase] = load(output / "summary.json")
            require(reports[phase]["status"] == "passed", f"Controles {phase} fallidos")
        return reports


def validate(destination):
    with TemporaryDirectory(prefix="petroandes-f11-") as directory:
        workspace = Path(directory)
        artifacts = workspace / "artifacts"
        require(not artifacts.exists(), "La validación exige un directorio de artefactos vacío")
        originals_before = originals()
        validation = Validation(destination, artifacts)
        summary = {"status": "failed", "cwd": str(Path.cwd()), "artefactos_inicialmente_ausentes": True,
                   "etapas": validation.steps}
        try:
            summary["inventario"] = validation.probes()
            summary["baseline"] = validation.rebuild(workspace)
            phases = validation.critical_controls()
            summary["laboratorio"] = {"inspector": phases["f7"]["inspector"], "herramientas": phases["f7"]["tools"],
                "proyeccion_reabierta": phases["f7"]["reopened_qdrant_points"],
                "casos_diagnosticos": phases["f8"]["casos_con_resultado"],
                "evaluacion_diagnostica": "f8/summary.json", "ataque": "f9/summary.json",
                "propagacion": "f10/summary.json", "revision_final_ensayo_f10": phases["f10"]["revision_final"]}
            audit = inventory(destination / "entrega")
            summary["evaluacion_formal"] = audit["evaluacion_formal"]
            summary["inventario_entrega"] = "entrega/summary.json"
            require(originals() == originals_before, "Cambió una fuente original durante el ensayo")
            summary["originales_verificados_sin_cambios"] = len(originals_before)
            summary["status"] = "passed"
        except (OSError, RuntimeError, ValueError, KeyError) as error:
            summary.update({"tipo": type(error).__name__, "motivo": str(error)})
    write_report(destination / "summary.json", summary)
    return 0 if summary["status"] == "passed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    destination = (APP_ROOT / parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    return validate(destination)


if __name__ == "__main__":
    raise SystemExit(main())
