"""Consolidación, cambios y consumo manual del outbox de PetroAndes."""
import argparse
import json
import sqlite3
from pathlib import Path

from f0_common import write_report
from petroandes.catalog.api import Catalog
from petroandes.catalog.store import document_key, index_directory, profile_path
from petroandes.catalog.substitution import substitute
from petroandes.deployment import LocalDeployment
from petroandes.extract.output import write_jsonl
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import DecisionRecord, Observation, Relation
from petroandes.governance.pdf_metadata import normalize, read_document
from petroandes.index.common import context_data, file_digest
from petroandes.index.propagation import MAX_ATTEMPTS, confirmed_event, propagate, rollback
from petroandes.index.stage import load_stage
from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path


def mutate(store, args):
    if args.action == "registrar-pdf":
        registry = json.loads((APP_ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
        pdf_root = relative_path(registry["corpus_pdf"], PROJECT_ROOT)
        path = relative_path(args.pdf, PROJECT_ROOT)
        if not path.is_relative_to(pdf_root) or path.suffix != ".pdf":
            raise ValueError("El PDF debe estar dentro del corpus configurado")
        doc, _ = read_document(path)
        revision = store.put_document(doc, args.revision)
    elif args.action == "decision":
        record = DecisionRecord.model_validate_json(args.entrada.read_text(encoding="utf-8"))
        if record.decision.estado == "certificado":
            snapshot = store.snapshot()
            doc = next((doc for doc in snapshot.documentos
                        if document_key(doc) == document_key(record.decision)), None)
            if (doc is None or not doc.pdf_uri.startswith("project:") or file_digest(relative_path(
                    doc.pdf_uri.removeprefix("project:"), PROJECT_ROOT)) != record.decision.pdf_sha256):
                raise ValueError("La decisión de autorización debe corresponder a un PDF verificado")
            if any(row.estado == "excluido" and document_key(row.documento) == document_key(doc)
                   and row.pdf_sha256 == doc.pdf_sha256 for row in snapshot.observaciones):
                raise ValueError("Una huella excluida por sustitución o derogación no se certifica")
        revision = store.apply_decision(record, args.revision)
    else:
        data = json.loads(args.entrada.read_text(encoding="utf-8"))
        observation = Observation.model_validate(data["observacion"])
        relation = Relation.model_validate(data["relacion"])
        docs = {document_key(doc): doc for doc in store.snapshot().documentos}
        for evidence in observation.fuentes:
            doc = docs[document_key(evidence.fuente)]
            if not doc.pdf_uri.startswith("project:"):
                raise ValueError("Referencia de PDF sin base de proyecto")
            source, pages = read_document(relative_path(doc.pdf_uri.removeprefix("project:"), PROJECT_ROOT))
            if (source != doc or evidence.pagina > len(pages)
                    or normalize(evidence.cita) not in normalize(pages[evidence.pagina - 1])):
                raise ValueError("La cita de sustitución no coincide con el PDF y la página")
        revision = substitute(store, observation, relation, data["revisor_humano"], args.revision)
    return {"status": "passed", "revision_gobierno": revision, "cambio": revision != args.revision,
            "catalogo": store.summary()}


def report_publication(destination, result, policy, encoder, stage):
    snapshot = result.pop("snapshot", None)
    events = result.pop("eventos")
    result["eventos_confirmados"] = len(events)
    result["archivos_eventos"] = write_jsonl(destination, "eventos", events)
    if snapshot is not None:
        receipt = result["recibo"]
        result["contexto"] = context_data(policy.context)
        result["bundle"] = {"fingerprint": encoder.fingerprint, **encoder.receipt}
        result["documentos_catalogo"] = len(snapshot.documentos)
        result["decisiones_catalogo"] = len(snapshot.decisiones)
        result["inventario"] = {
            "documentos": write_jsonl(destination, "documentos", [doc.model_dump(mode="json")
                                                                  for doc in snapshot.documentos]),
            "decisiones": write_jsonl(destination, "decisiones", [row.decision.model_dump(mode="json")
                                                                  for row in snapshot.decisiones]),
        }
        root = index_directory(snapshot.perfil)
        folder = root / "generations" / receipt["key"]["generation_id"]
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        ids = manifest.pop("fragmentos")
        result["inventario"]["fragmentos"] = write_jsonl(destination, "fragmentos", [{"chunk_id": cid} for cid in ids])
        write_report(destination / "manifiesto.json", manifest | {"cantidad_fragmentos": len(ids),
                     "stage": stage.manifest["generation_id"], "manifiesto_sha256": receipt["manifest_sha256"]}, emit=False)
    return result


def update_index(store, args, destination):
    event_revision = getattr(args, "evento", None)
    replay = confirmed_event(store, event_revision)
    if replay is not None:
        replay.pop("eventos")
        return replay | {"eventos_confirmados": 0, "archivos_eventos": []}
    deployment = LocalDeployment(args.profile)
    policy = EligibilityService(store, deployment.context)
    encoder = deployment.encoder
    if args.action == "revertir":
        return rollback(deployment.index, policy, encoder, args.generation)
    label = getattr(args, "operacion", None)
    if label is not None and (not label.strip() or len(label) > 100):
        raise ValueError("La operación de reindexación requiere un identificador de 1 a 100 caracteres")
    if args.stage is None:
        raise ValueError("Se requiere --stage para publicar la revisión vigente")
    stage = load_stage(args.stage.resolve(), encoder.tokenizer)
    result = propagate(deployment.index, policy, encoder, stage, attempts=args.intentos,
                       event_revision=event_revision, reindex=label)
    return report_publication(destination, result, policy, encoder, stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("baseline", "laboratorio"), default="laboratorio")
    parser.add_argument("--output-dir", type=Path, required=True)
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("registrar-pdf", "decision", "sustituir"):
        sub = actions.add_parser(name)
        sub.add_argument("--revision", type=int, required=True)
        sub.add_argument("pdf" if name == "registrar-pdf" else "entrada",
                         type=str if name == "registrar-pdf" else Path)
    for name in ("consolidar", "propagar", "reindexar"):
        sub = actions.add_parser(name)
        sub.add_argument("--stage", type=Path, required=name != "propagar")
        sub.add_argument("--intentos", type=int, default=MAX_ATTEMPTS)
        if name == "propagar":
            sub.add_argument("--evento", type=int)
        if name == "reindexar":
            sub.add_argument("--operacion", required=True)
    actions.add_parser("revertir").add_argument("generation")
    args = parser.parse_args()
    destination = (APP_ROOT / args.output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    try:
        with Catalog.open(profile_path(args.profile), args.profile) as store:
            if args.action in ("registrar-pdf", "decision", "sustituir"):
                if args.profile != "laboratorio":
                    raise ValueError("Los cambios de F10 se registran únicamente en laboratorio")
                result = mutate(store, args)
            else:
                result = update_index(store, args, destination)
    except (OSError, sqlite3.Error, RuntimeError, ValueError, KeyError) as error:
        result = {"status": "failed", "tipo": type(error).__name__, "motivo": str(error)}
    write_report(destination / "summary.json", {"operacion": args.action, "perfil": args.profile, **result})
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
