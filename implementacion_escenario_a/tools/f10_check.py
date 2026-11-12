"""Ejecuta y documenta F10 con copias de los PDF y del catálogo histórico."""
import argparse
import math
import platform
import sys
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from time import perf_counter

import psutil
from pytest import MonkeyPatch

from f0_common import configure_cache, write_report
from f10_controls import CODE, QUESTION, decision, denied_routes, fixture_document, live_receipt, publish, race_revoke
from petroandes.extract import pipeline
from petroandes.extract.output import write_jsonl
from petroandes.governance import pdf_metadata
from petroandes.index import stage
from petroandes.index.common import IndexUnavailable, file_digest
from petroandes.index.propagation import rollback
from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path

sys.path.insert(0, str(APP_ROOT / "tests"))
from historical_lab import historical_workspace


def measured(values, target):
    percentile = sorted(values)[math.ceil(len(values) * 0.95) - 1]
    return {"n": len(values), "muestras_s": values, "p95_observado_s": percentile, "objetivo_s": target,
            "dentro_del_objetivo_en_la_muestra": percentile <= target}


def expiry(service, source, fragment, document, destination, patch):
    expiry_at = next(row.decision.effective_to for row in service.policy.catalog.snapshot().decisiones
                     if row.decision.doc_id == document.doc_id)
    before = live_receipt(service)
    with patch.context() as scoped:
        scoped.setattr(service.policy, "clock", lambda: expiry_at)
        routes = denied_routes(service, fragment, destination, "vencimiento-tres-rutas")
        assert routes["busqueda"]["revision_gobierno"] == 13
        try:
            rollback(service.root, service.policy, service.encoder, before["key"]["generation_id"])
        except IndexUnavailable as error:
            write_report(destination / "rollback-vencido.json", {"motivo": str(error)}, emit=False)
        else:
            raise AssertionError("La reversión reutilizó permisos vencidos")
        expired = publish(service, source, destination, "vencimiento-propagado")
        assert expired["publicacion"]["published_fragments"] == 0 and expired["eventos"] == []
    # El reloj vuelve al punto inicial solo en este ensayo desechable.
    restored = publish(service, source, destination, "restablecer-reloj-ensayo")
    assert restored["publicacion"]["generation_id"] == before["key"]["generation_id"]


def authorize_again(service, source, document, destination):
    store = service.policy.catalog
    approved_at = decision(store, document, "reaprobacion")
    published = publish(service, source, destination, "aprobacion")
    assert published["status"] == "passed" and published["publicacion"]["published_fragments"] == 58
    assert service.search(QUESTION)["resultado"]["estado"] == "recuperada"
    return perf_counter() - approved_at


def change_permissions(service, source, fragment, destination):
    store = service.policy.catalog
    other = fixture_document(store, fragment["doc_id"])
    decision(store, other, "permisos", grupos=("GRUPO-SIN-ACCESO-F10",))
    denied_routes(service, fragment, destination, "permisos-tres-rutas")
    published = publish(service, source, destination, "permisos-propagados")
    assert published["vectores_calculados"] == 0 and published["vectores_reutilizados"] > 0
    denied_routes(service, fragment, destination, "permisos-despues")
    assert service.search(QUESTION)["resultado"]["estado"] == "recuperada"


def change_pdf(service, workspace, fixture_root, document, fragment, destination):
    store = service.policy.catalog
    relative = document.pdf_uri.removeprefix("project:")
    path = relative_path(relative, fixture_root)
    original = relative_path(relative, PROJECT_ROOT)
    before = file_digest(original)
    with path.open("ab") as target:
        target.write(b"\n% fixture F10: huella modificada para ensayo\n")
    changed, _ = pdf_metadata.read_document(path)
    assert changed.pdf_sha256 != document.pdf_sha256
    revision = store.put_document(changed, store.verify_revision())
    assert store.put_document(changed, revision) == revision
    assert all(doc.doc_id != CODE for doc in service.policy.eligible().documentos)
    denied_routes(service, fragment, destination, "huella-cambiada-tres-rutas")
    manifest = workspace / "f3-nueva-huella/manifest.json"
    pipeline.ingest("laboratorio", manifest.parent)
    source = stage.load_stage(manifest, service.encoder.tokenizer)
    after = publish(service, source, destination, "huella-pendiente-propagada")
    assert after["status"] == "passed" and after["vectores_calculados"] == 0
    denied_routes(service, fragment, destination, "huella-pendiente-despues")
    assert file_digest(original) == before
    write_report(destination / "huellas-pdf.json", {"pdf_uri": document.pdf_uri, "original": before,
                 "copia_modificada": changed.pdf_sha256, "revision": revision, "elegible": False}, emit=False)
    return source


def reindex(service, source, destination):
    before = live_receipt(service)
    rebuilt = publish(service, source, destination, "reindexacion", reindex="reconstruccion-f10")
    assert rebuilt["status"] == "passed"
    assert rebuilt["publicacion"]["collection"] != before["collection"]
    assert rebuilt["comparacion"]["entradas_identicas"] == rebuilt["publicacion"]["published_fragments"]
    assert rebuilt["vectores_reutilizados"] == 0 and rebuilt["vectores_calculados"] > 0
    previous = before["key"]["generation_id"]
    saved = rollback(service.root, service.policy, service.encoder, previous)
    write_report(destination / "rollback-misma-revision.json", saved, emit=False)
    assert live_receipt(service) == before


def run(destination, workspace, patch):
    fixture_root = workspace / "proyecto"
    copytree(PROJECT_ROOT / "corpus", fixture_root / "corpus")
    for module in (pipeline, stage, pdf_metadata):
        patch.setattr(module, "PROJECT_ROOT", fixture_root)
    with historical_workspace(workspace, patch) as (service, source):
        store = service.policy.catalog
        snapshot = store.snapshot()
        document = fixture_document(store, CODE)
        fragments = [item["fragment"] for item in source.records]
        reference = next(row for row in fragments if row["doc_id"] == CODE and row["section_id"] == "2")
        other = next(row for row in fragments if row["doc_id"] == "RES-CREG-0043-2024" and row["section_id"] == "articulo-2")
        consolidated = publish(service, source, destination, "consolidacion")
        assert consolidated["status"] == "passed" and consolidated["publicacion"]["published_fragments"] == 58
        assert len(consolidated["eventos"]) == 13 and len(snapshot.documentos) == 19
        write_jsonl(destination, "documentos-iniciales", [doc.model_dump(mode="json") for doc in snapshot.documentos])
        write_jsonl(destination, "decisiones-iniciales", [row.decision.model_dump(mode="json")
                                                         for row in snapshot.decisiones])
        write_report(destination / "bundle.json", {"fingerprint": service.encoder.fingerprint,
                     **service.encoder.receipt}, emit=False)
        repeated = publish(service, source, destination, "consolidacion-repetida")
        assert repeated["publicacion"]["reused"] and repeated["eventos"] == []
        assert service.search(QUESTION)["resultado"]["estado"] == "recuperada"
        warm = []
        for _ in range(5):
            query = service.search(QUESTION)
            assert query["resultado"]["estado"] == "recuperada"
            warm.append(query["traza"]["tiempos_ms"]["total"] / 1000)
        expiry(service, source, reference, document, destination, patch)
        revoked = race_revoke(service, source, destination, reference, workspace / "review.sqlite3", patch)
        approved = authorize_again(service, source, document, destination)
        change_permissions(service, source, other, destination)
        changed_stage = change_pdf(service, workspace, fixture_root, document, reference, destination)
        reindex(service, changed_stage, destination)
        denied_routes(service, reference, destination, "huella-pendiente-tras-rollback")
        return {"status": "passed", "documentos_catalogo": len(snapshot.documentos),
                "fragmentos_iniciales": 58, "revision_inicial": 13, "revision_final": store.verify_revision(),
                "eventos_pendientes": len(store.pending_events()),
                "mediciones": {"consulta_caliente": measured(warm, 3),
                               "revocacion": measured([revoked], 60), "aprobacion": measured([approved], 900)},
                "equipo": {"plataforma": platform.platform(), "cpus_logicas": psutil.cpu_count(),
                           "ram_bytes": psutil.virtual_memory().total},
                "alcance": "muestras técnicas en Docker, con reindexación del bundle E5 fijado"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    destination = (APP_ROOT / parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    try:
        configure_cache(offline=True)
        with TemporaryDirectory(prefix="petroandes-f10-") as directory, MonkeyPatch.context() as patch:
            summary = run(destination, Path(directory), patch)
    except (AssertionError, OSError, RuntimeError, ValueError, KeyError, StopIteration) as error:
        summary = {"status": "failed", "tipo": type(error).__name__, "motivo": str(error)}
        write_report(destination / "summary.json", summary)
        raise
    write_report(destination / "summary.json", summary)


if __name__ == "__main__":
    main()
