"""Reapertura y copia coherente de las ramas reconciliadas, sin cambiar contexto."""
import argparse
import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path, index_directory
from petroandes.embeddings.encoder import E5Encoder
from petroandes.extract.output import write_json
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index.common import file_digest
from petroandes.index.publication import Publisher
from petroandes.index.stage import load_stage
from petroandes.paths import APP_ROOT
from f0_common import configure_cache


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    configure_cache(offline=True)
    encoder = E5Encoder()
    context = ServiceContext.model_validate_json((APP_ROOT / "config/f4-context.json").read_text())
    root = index_directory("laboratorio")
    with Catalog.open(profile_path("laboratorio"), "laboratorio") as catalog:
        before = catalog.summary()
        policy = EligibilityService(catalog, context)
        with Publisher(root, policy, encoder) as publisher:
            manifest, receipt = publisher.active()
            assert manifest.revision_gobierno == 13 and manifest.fragmentos == ()
            assert policy.eligible().documentos == ()
            repeat = publisher.publish(load_stage(args.stage.resolve(), encoder.tokenizer))
            assert repeat["reused"] and repeat["generation_id"] == manifest.generation_id
            assert publisher.active()[0] == manifest
            points = publisher.owner.client.count(receipt["collection"], exact=True).count
            assert points == 0
        # Solo copias SQLite/manifiestos inmutables y backup SQLite, con propietario cerrado.
        folder = root / "generations" / manifest.generation_id
        for name in ("manifest.json", "receipt.json", "catalog.sqlite3", "lexical.sqlite3"):
            shutil.copyfile(folder / name, destination / name)
        with closing(sqlite3.connect(root / "publications.sqlite3")) as source:
            with closing(sqlite3.connect(destination / "publications.sqlite3")) as copy:
                source.backup(copy)
        assert catalog.summary() == before
    report = {"status": "passed", "perfil": "laboratorio", "governance_revision": 13,
        "generation_id": manifest.generation_id, "collection": receipt["collection"],
        "fragments": 0, "dense_points": points, "idempotent": True,
        "service_context_unchanged": True, "service_context": context.model_dump(mode="json"),
        "reason": "Ámbito/grupo del servicio distintos del permiso de revisión; no ampliar acceso",
        "outbox_events_pending": before["eventos_pendientes"],
        "sha256": {path.name: file_digest(path) for path in sorted(destination.iterdir())}}
    write_json(destination / "summary.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
