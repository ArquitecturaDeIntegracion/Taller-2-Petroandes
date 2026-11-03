"""Inspecciona dependencias administrativas de casos; no usa ni cambia oráculos."""
import argparse
import json
from pathlib import Path

from petroandes.extract.output import write_json, write_jsonl
from petroandes.governance.administration import load_request
from petroandes.paths import APP_ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    request = load_request(args.request)
    certified = {(spec.doc_id, spec.version_documental) for spec in request.documentos}
    proposals = {}
    for path in (APP_ROOT / "docs/revision/decisiones").glob("*.json"):
        item = json.loads(path.read_text(encoding="utf-8"))
        document = item["documento"]
        proposals[item["id"]] = (document["doc_id"], document["version_documental"])
    rows = []
    for path in sorted((APP_ROOT / "docs/revision/casos").glob("*.json")):
        # El oráculo permanece sin ejecutar ni ajustar; leer solo dependencias/revisión.
        data = json.loads(path.read_text(encoding="utf-8"))
        required = data["precondiciones"]["propuestas_documentales_requeridas"]
        missing = [code for code in required if proposals[code] not in certified]
        rows.append({"case_id": data["case_id"], "required_proposals": required,
            "missing_certifications": missing, "missing_documents": [proposals[code][0] for code in missing],
            "human_review": data["revision_humana"]["estado"],
            "execution": data["estado_ejecucion"], "frozen": data["congelado_para_evaluacion"],
            "automatic_approval": False})
    args.output.mkdir(parents=True, exist_ok=False)
    write_jsonl(args.output, "dependencies", rows)
    report = {"cases": len(rows), "human_review_pending": sum(
        row["human_review"] == "pendiente_revision" for row in rows),
        "missing_certification_cases": [row["case_id"] for row in rows if row["missing_certifications"]],
        "approved_cases": 0, "executed_cases": 0, "frozen_cases": 0,
        "method": "Solo metadatos de dependencias; no se aprueban ni reescriben respuestas esperadas"}
    write_json(args.output / "summary.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
