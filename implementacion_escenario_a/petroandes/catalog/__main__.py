"""CLI administrativa F2: inicializar/inspeccionar; no importa certificaciones humanas."""
import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from contextlib import closing

from petroandes.governance.baseline import load_baseline
from petroandes.paths import APP_ROOT, ARTIFACTS_DIR, portable
from .api import Catalog
from .store import index_directory, profile_path


def save(path, data):
    text = json.dumps(portable(data), ensure_ascii=False, indent=2) + "\n"
    if len(text.splitlines()) > 200:
        raise ValueError("Dividir informe de más de 200 líneas")
    with path.open("x", encoding="utf-8") as output:
        output.write(text)


def export(catalog, destination, corpus, observations, relations):
    destination.mkdir(parents=True, exist_ok=False)
    for name, items in (("documents", corpus), ("observations", observations), ("relations", relations)):
        folder = destination / name
        folder.mkdir()
        for index, item in enumerate(items, 1):
            save(folder / f"{index:02d}.json", item.model_dump(mode="json"))
    backup = destination / "catalog.sqlite3"
    with closing(sqlite3.connect(backup)) as copy:
        catalog.db.backup(copy)
    report = {"evidence_schema_version": 2, "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "operacion": "carga_inicial_f2_desde_pdf", **catalog.summary(),
              "relaciones": len(relations), "certificaciones_humanas_creadas": 0,
              "backup_sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
              "catalog_ref": {"base": "artifacts", "path":
                              f"catalog/{catalog.perfil}/catalog.sqlite3"},
              "index_ref": {"base": "artifacts", "path":
                            index_directory(catalog.perfil).relative_to(ARTIFACTS_DIR).as_posix()},
              "indices_construidos": False}
    save(destination / "summary.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "status"])
    parser.add_argument("--profile", choices=["baseline", "laboratorio"], default="baseline")
    parser.add_argument("--evidence-dir")
    args = parser.parse_args()
    path = profile_path(args.profile)
    if args.command == "init":
        if not args.evidence_dir:
            parser.error("init requiere --evidence-dir nuevo para conservar la carga")
        destination = APP_ROOT / args.evidence_dir
        if destination.exists() or path.exists():
            parser.error("Catálogo/evidencia existente; no se sobrescribe ni reinicia")
        corpus, observations, relations = load_baseline()
        with Catalog.create(path, args.profile) as catalog:
            catalog.seed(corpus, observations, relations)
            report = export(catalog, destination, corpus, observations, relations)
    else:
        with Catalog.open(path, args.profile, read_only=True) as catalog:
            report = catalog.summary()
    print(json.dumps(portable(report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
