"""Comprueba una copia extraída de la entrega con el baseline y MCP real."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import MonkeyPatch

from f0_common import configure_cache, write_report
from f11_check import Validation, require
from f7_inspector import QUESTION, SEARCH, equivalent, fixture_config, historical_lab, validated, verify_list
from f7_inspector_client import Inspector
from petroandes.compose import answer
from petroandes.contracts.queries import SearchQuery
from petroandes.paths import APP_ROOT


def check(destination, workspace):
    baseline = Validation(destination, workspace / "artefactos").rebuild(workspace)
    historical = workspace / "historico"
    historical.mkdir()
    inspector_dir = destination / "inspector"
    inspector_dir.mkdir()
    with MonkeyPatch.context() as patch, historical_lab(historical, patch) as (service, _):
        inspector = Inspector(historical, inspector_dir)
        inspector.configure(fixture_config(historical, service))
        tools = verify_list(inspector)
        reply, _ = inspector.run("p101", "historico", tool=SEARCH, arguments=QUESTION)
        result = validated(reply, SEARCH, tools)
        equivalent(result, answer(service, SearchQuery.model_validate(QUESTION))["resultado"])
        require(result["estado"] == "respondida" and result["revision_gobierno"] == 13,
                "La consulta histórica no devolvió la respuesta esperada")
        excerpts = " ".join(claim["texto"] for claim in result["afirmaciones"])
        require("1.180 psi" in excerpts and "1.240 psi" in excerpts, "Faltan los valores de la ficha P-101")
    return {"status": "passed", "baseline": baseline, "inspector": inspector.version,
            "herramientas": list(tools), "estado_p101": result["estado"],
            "revision_historica": result["revision_gobierno"], "paridad_python_mcp": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    destination = (APP_ROOT / parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    configure_cache(offline=True)
    try:
        with TemporaryDirectory(prefix="petroandes-entrega-") as folder:
            summary = check(destination, Path(folder))
    except (AssertionError, KeyError, OSError, RuntimeError, ValueError) as error:
        write_report(destination / "summary.json", {"status": "failed", "tipo": type(error).__name__,
                     "motivo": str(error)})
        raise
    write_report(destination / "summary.json", summary)


if __name__ == "__main__":
    main()
