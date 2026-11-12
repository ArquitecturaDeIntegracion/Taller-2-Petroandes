"""Prepara catálogos y contextos independientes a partir de la revisión congelada."""
import argparse
import json
from datetime import timedelta
from pathlib import Path
from shutil import copyfile

from review_frozen import APP_ROOT, CONFIRMED, EVIDENCE, clock_for, context_for, load, require, verify
from petroandes.catalog.api import Catalog
from petroandes.extract.output import write_json, write_jsonl
from petroandes.governance.models import Conflict, DecisionRecord
from petroandes.index.common import file_digest

HISTORICAL = APP_ROOT / "evidence/lab/20261103/registration"


def verified_backup(folder, name, hash_field):
    path = folder / name
    require(file_digest(path) == load(folder / "summary.json")[hash_field][name],
            f"Copia de gobierno inválida: {name}")
    return path


def authority(registration):
    updated = verified_backup(registration, "laboratorio-after.sqlite3", "sha256_copias")
    with Catalog.open(updated, "laboratorio", read_only=True) as store:
        snapshot = store.snapshot()
    require(snapshot.revision == 15 and len(snapshot.decisiones) == 14,
            "La copia de autoridad debe contener el lote de manuales verificado")
    return {(row.decision.doc_id, row.decision.version_documental, row.decision.pdf_sha256): row
            for row in snapshot.decisiones}


def decision_for(proposal, records):
    source = load(CONFIRMED.parent / f"decisiones/{proposal}.json")["documento"]["pdf"]
    identity = (source["doc_id"], source["version_documental"], source["pdf_sha256"])
    record = records[identity]
    require(record.decision.estado == "certificado", f"Falta autorización de {proposal}")
    return record


def seed_catalog(case, records, source, path, profile):
    copyfile(source, path)
    used = {}
    when = clock_for(case)
    with Catalog.open(path, profile) as store:
        require(store.verify_revision() == 1, "La semilla original debe estar en revisión 1")
        for proposal in case["precondiciones"]["propuestas_documentales_requeridas"]:
            original = decision_for(proposal, records)
            decision = original.decision
            probe_time = when - timedelta(microseconds=1) if case["case_id"] == "R11" else when
            require(max(decision.effective_from, decision.revisado_en) <= probe_time < decision.effective_to,
                    f"El reloj de la copia no coincide con la ventana certificada: {proposal}")
            require(all(call["uso"] in decision.usos for call in case["llamadas_principales"]),
                    f"Falta uso autorizado en la copia: {proposal}")
            # La decisión conserva la identidad original; la revisión es local a esta copia.
            data = original.model_dump()
            revision = store.verify_revision()
            data["decision"]["revision_gobierno"] = revision + 1
            store.apply_decision(DecisionRecord.model_validate(data), revision)
            used[proposal] = {"id": decision.decision_id, "revision_fuente": decision.revision_gobierno,
                              "revision_local": revision + 1, "pdf_sha256": decision.pdf_sha256}
        if case["case_id"] == "R12":
            context = context_for(case)
            docs = [decision_for(key, records).decision for key in used]
            conflict = Conflict(conflict_id="R12-conflicto-sintetico", ambito=context.ambito, uso=context.uso,
                documentos=[{"doc_id": doc.doc_id, "version_documental": doc.version_documental} for doc in docs],
                fundamento="Conflicto de gobierno simulado para la reserva R12.",
                registrado_por="Preparación del fixture académico R12",
                effective_from=when - timedelta(hours=1), effective_to=when + timedelta(hours=1))
            store.add_conflict(conflict, store.verify_revision())
        summary = store.summary()
    require(summary["decisiones_registradas"] == len(used) and summary["documentos"] == 19
            and summary["clasificacion"]["excluido"] == 4, "La semilla heredó contenido o permisos inesperados")
    return summary, used


def operations(case):
    key = case["case_id"]
    if key == "R09":
        return {"control_previo": {"consulta": "Umbral de alarma de presión de Ayacucho–Coveñas en PRO-OPE-012 v3",
                                   "top_k": 5},
                "mutacion_posterior": "revocar D08 después de publicar y verificar el vector inicial",
                "obtencion_posterior": {"doc_id": "PRO-OPE-012", "version_documental": "3", "section_id": "3"},
                "expansion_f5": {"chunk_id_desde": "fragmento_del_control_previo"}}
    if key == "R10":
        return {"control_previo": {"doc_id": "PRO-MED-007", "version_documental": "2", "section_id": "3",
                                   "pdf_sha256_desde": "autorizaciones/D06/pdf_sha256"},
                "mutacion_posterior": "registrar el PDF derivado en el catálogo aislado sin certificar",
                "obtencion_posterior": {"doc_id": "PRO-MED-007", "version_documental": "2", "section_id": "3",
                                        "pdf_sha256_desde": "sha256_del_pdf_derivado"}}
    if key == "R11":
        return {"control_previo_reloj": (clock_for(case) - timedelta(microseconds=1)).isoformat()}
    if key == "R12":
        return {"conflicto_sembrado": "R12-conflicto-sintetico"}
    return {}


def prepare(output, registration):
    verified, cases = verify()
    seeds = {profile: verified_backup(HISTORICAL, f"{profile}-before.sqlite3", "backup_sha256")
             for profile in ("baseline", "laboratorio")}
    records = authority(registration)
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for case in cases:
        key = case["case_id"]
        folder = output / key
        folder.mkdir()
        db = folder / "catalog.sqlite3"
        profile = case["contexto_servicio_solo_fixture"]["perfil"]
        summary, used = seed_catalog(case, records, seeds[profile], db, profile)
        contexts = {call["id"]: {"config": context_for(case, call["uso"]).model_dump(mode="json"),
                                 "ruta_indice_relativa": f"index/{call['id']}"}
                    for call in case["llamadas_principales"]}
        config = {"case_id": key, "perfil": profile, "reloj_simulado": clock_for(case).isoformat(),
                  "catalogo": "catalog.sqlite3", "contextos": contexts, "autorizaciones": used,
                  "preparacion_adicional": operations(case)}
        write_json(folder / "contextos.json", config)
        rows.append({"id": key, "particion": case["particion"],
                     "catalogo_sha256": file_digest(db), "contextos_sha256": file_digest(folder / "contextos.json"),
                     "catalogo": summary, "contextos": list(contexts), "busquedas_ejecutadas": 0})
    names = write_jsonl(output, "semillas", rows)
    result = verified | {"copias_aisladas": len(rows), "contextos_preparados": sum(len(row["contextos"]) for row in rows),
                         "semillas": names, "fase": "catálogos y contextos de preparación",
                         "publicacion_indices": "pendiente_en_ejecucion_posterior"}
    write_json(output / "summary.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.output_dir, EVIDENCE / "registro"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
