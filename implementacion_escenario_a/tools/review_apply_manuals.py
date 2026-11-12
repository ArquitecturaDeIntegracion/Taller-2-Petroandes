"""Aplica el lote humano de dos manuales y conserva su comprobación de permisos."""
import argparse
import json
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import get_args

from certify_lab import backup
from check_lab_state import baseline_identity
from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path
from petroandes.contracts.common import Use
from petroandes.extract.output import write_json, write_jsonl
from petroandes.governance.administration import load_request, request_digest
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.governance.registration import real_clock, register
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT

FOLDER = APP_ROOT / "docs/revision/20261108-confirmada"
REQUEST = APP_ROOT / "config/admin/lab-20261108/request/request.json"
EVIDENCE = APP_ROOT / "evidence/revision/20261108-confirmada"


def proposals():
    return {key: json.loads((FOLDER.parent / f"decisiones/{key}.json").read_text(encoding="utf-8"))
            for key in ("D01", "D02", "D03")}


def check_request(request, manuals, store):
    ids = {(row["documento"]["doc_id"], row["documento"]["version_documental"]): row
           for key, row in manuals.items() if key != "D03"}
    if (request.revisor_humano != "Jonnathan Caballero" or len(request.documentos) != 2
            or request.effective_to.isoformat() != "2026-12-01T00:00:00-05:00"
            or request.autorizacion.path != "docs/revision/20261108-confirmada/autorizacion.md"
            or request.grupos != ("LAB_REVISION",)
            or request.ambito.model_dump() != {"tipo": "general", "identificador": "corpus_revision"}):
        raise ValueError("El lote no coincide con la confirmación humana")
    current = {(doc.doc_id, doc.version_documental): doc.pdf_sha256 for doc in store.snapshot().documentos}
    for spec in request.documentos:
        identity = (spec.doc_id, spec.version_documental)
        item = ids[identity]
        if (spec.usos != ("evidencia_historica",)
                or spec.rol_area_simulado != item["propuesta"]["rol_emisor_simulado_a_confirmar"]
                or current[identity] != item["documento"]["pdf"]["pdf_sha256"]):
            raise ValueError("Identidad, huella o uso del manual fuera de la confirmación humana")


def verify_permissions(store, request, records, manuals):
    start = records[0].decision.effective_from
    watched = {item["documento"]["doc_id"] for item in manuals.values()}
    allowed = watched - {"MAN-OPE-004"}
    historical = ServiceContext(identidad="sonda-revision-manuales", grupos=frozenset(request.grupos),
                                ambito=request.ambito, uso="evidencia_historica")

    def eligible(context, when):
        result = EligibilityService(store, context, clock=lambda: when).eligible()
        return sorted(doc.doc_id for doc in result.documentos if doc.doc_id in watched)

    checks = {"historico": eligible(historical, start),
              "antes": eligible(historical, start - timedelta(microseconds=1)),
              "fin_exclusivo": eligible(historical, request.effective_to),
              "otro_grupo": eligible(historical.model_copy(update={"grupos": frozenset({"LAB_SIN_ACCESO"})}), start),
              "otro_ambito": eligible(historical.model_copy(update={
                  "ambito": historical.ambito.model_copy(update={"identificador": "lectura-documental-educativa"})}),
                  start)}
    for usage in get_args(Use):
        if usage != historical.uso:
            checks[usage] = eligible(historical.model_copy(update={"uso": usage}), start)
    if set(checks["historico"]) != allowed or any(value for key, value in checks.items() if key != "historico"):
        raise ValueError("La comprobación de los límites del permiso falló")
    return checks


def run(destination):
    request = load_request(REQUEST)
    now = real_clock()
    baseline = baseline_identity()
    write_json(destination / "baseline-antes.json", baseline)
    if now >= request.effective_to:
        return {"status": "ventana_vencida", "aplicacion": "pendiente_nueva_fecha_autorizada",
                "fin_exclusivo": request.effective_to.isoformat()}
    manuals = proposals()
    with Catalog.open(profile_path("laboratorio"), "laboratorio") as store:
        before = store.summary()
        check_request(request, manuals, store)
        backup(store, destination / "laboratorio-before.sqlite3")
        records, reused = register(store, request, clock=lambda: now)
        backup(store, destination / "laboratorio-after.sqlite3")
        (destination / "decisions").mkdir()
        for offset, record in enumerate(records, 1):
            write_json(destination / "decisions" / f"{offset:02d}.json", record.model_dump(mode="json"))
        write_jsonl(destination, "eventos", [{"revision": rev, "tipo": kind, "payload": json.loads(payload)}
                    for rev, kind, payload in store.db.execute(
                        "SELECT revision,kind,payload FROM events WHERE revision>? ORDER BY revision",
                        (request.expected_revision,))])
        after = store.summary()
        if after["clasificacion"] != {"pendiente": 1, "certificado": 14, "excluido": 4}:
            raise ValueError("Clasificación inesperada después de registrar los manuales")
        permissions = verify_permissions(store, request, records, manuals)
    current_baseline = baseline_identity()
    write_json(destination / "baseline-despues.json", current_baseline)
    if current_baseline != baseline:
        raise ValueError("La identidad de baseline cambió durante la operación")
    return {"status": "passed", "reutilizado": reused, "solicitud_sha256": request_digest(request),
            "revision_humana_fecha": "2026-11-08", "inicio_efectivo": records[0].decision.effective_from.isoformat(),
            "fin_exclusivo": request.effective_to.isoformat(), "antes": before, "despues": after,
            "baseline_identico": True, "permisos_manuales": permissions,
            "sha256_copias": {path.name: file_digest(path) for path in destination.glob("*.sqlite3")}}


def probe_index(stage_path):
    """Comprueba la lectura de ambos manuales en un índice separado del servicio."""
    from petroandes.contracts.queries import FragmentQuery
    from petroandes.deployment import LocalDeployment
    from petroandes.index.publication import Publisher
    from petroandes.index.stage import load_stage
    from petroandes.retrieve import Retriever

    registration = json.loads((EVIDENCE / "registro/summary.json").read_text(encoding="utf-8"))
    baseline = json.loads((EVIDENCE / "registro/baseline-antes.json").read_text(encoding="utf-8"))
    request = load_request(REQUEST)
    deployment = LocalDeployment("laboratorio")
    encoder = deployment.encoder
    stage = load_stage(stage_path.resolve(), encoder.tokenizer)
    context = ServiceContext(identidad="sonda-documental-manuales", grupos=frozenset(request.grupos),
                             ambito=request.ambito, uso="evidencia_historica")
    when = real_clock()
    reads = {}
    with TemporaryDirectory(prefix="petroandes-manuales-") as folder:
        with Catalog.open(deployment.catalog_path, "laboratorio", read_only=True) as store:
            root = Path(folder) / "index"
            policy = EligibilityService(store, context, clock=lambda: when)
            with Publisher(root, policy, encoder) as publisher:
                publication = publisher.publish(stage)
            reader = Retriever(root, policy, encoder)
            for key, section in (("D01", "2"), ("D02", "1")):
                ref = proposals()[key]["documento"]["pdf"]
                query = FragmentQuery(**{name: ref[name] for name in
                    ("doc_id", "version_documental", "pdf_sha256")}, section_id=section)
                result = reader.obtain(query)["resultado"]
                if result["estado"] != "encontrado" or any(
                        row["pdf_sha256"] != query.pdf_sha256 for row in result["citas"]):
                    raise ValueError(f"Lectura administrativa fallida: {key}")
                reads[key] = {"estado": result["estado"], "citas": result["citas"]}
            summary = store.summary()
    if (summary["governance_revision"] != registration["despues"]["governance_revision"]
            or summary["eventos_pendientes"] != 0 or baseline_identity() != baseline):
        raise ValueError("No se pudo verificar la propagación o la identidad de baseline")
    return {"status": "passed", "catalogo": summary, "baseline_identico": True,
            "contexto": context.model_dump(mode="json"), "publicacion_aislada": publication,
            "obtenciones_administrativas": reads, "casos_ejecutados": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stage", type=Path, help="Solo sondea el índice autorizado con el staging indicado")
    args = parser.parse_args()
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    report = probe_index(args.stage) if args.stage else run(destination)
    write_json(destination / "summary.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
