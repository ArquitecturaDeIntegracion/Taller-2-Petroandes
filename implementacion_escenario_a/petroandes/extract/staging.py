"""Generación SQLite completa y aislada; nunca activa índices ni modifica gobierno."""
import hashlib
import json
import os
import sqlite3
from contextlib import closing
from tempfile import TemporaryDirectory

from petroandes.paths import ARTIFACTS_DIR
from .models import ExtractionReview
from .output import write_json


def record_digest(record):
    if not isinstance(record, dict) or not isinstance(record.get("metadata"), dict):
        raise ExtractionReview("Estructura de payload inválida en staging")
    stable = dict(record)
    stable["metadata"] = {key: value for key, value in record["metadata"].items() if key != "ingested_at"}
    return hashlib.sha256(json.dumps(stable, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def verify_existing(path, manifest, records, parents):
    database = path / "fragments.sqlite3"
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        saved = db.execute("SELECT payload FROM manifest WHERE singleton=1").fetchone()
        if not saved or json.loads(saved[0]) != manifest:
            raise ExtractionReview("Generación existente incompleta o con manifiesto diferente")
        actual = {}
        for key, digest, payload in db.execute("SELECT chunk_id,digest,payload FROM fragments"):
            try:
                computed = record_digest(json.loads(payload))
            except (ValueError, KeyError, TypeError) as exc:
                raise ExtractionReview("Payload de fragmento inválido en staging") from exc
            if computed != digest:
                raise ExtractionReview("Payload de fragmento corrupto en staging")
            actual[key] = digest
        expected = {record["fragment"]["chunk_id"]: record_digest(record) for record in records}
        actual_parents = {key: json.loads(payload) for key, payload in db.execute("SELECT * FROM parents")}
        expected_parents = {parent["parent_id"]: json.loads(json.dumps(parent)) for parent in parents}
        if actual != expected or actual_parents != expected_parents:
            raise ExtractionReview("Generación existente no coincide; no sobrescribir")


def store_generation(manifest, records, parents):
    base = ARTIFACTS_DIR / "ingest" / manifest["perfil"]
    base.mkdir(parents=True, exist_ok=True)
    target = base / manifest["generation_id"]
    if target.exists():
        verify_existing(target, manifest, records, parents)
        return target, True
    with TemporaryDirectory(prefix="staging-", dir=base) as temporary:
        from pathlib import Path

        temporary = Path(temporary)
        with closing(sqlite3.connect(temporary / "fragments.sqlite3")) as db, db:
            db.executescript("""
                CREATE TABLE manifest(singleton INTEGER PRIMARY KEY CHECK(singleton=1), payload TEXT NOT NULL);
                CREATE TABLE parents(parent_id TEXT PRIMARY KEY,payload TEXT NOT NULL);
                CREATE TABLE fragments(chunk_id TEXT PRIMARY KEY,parent_id TEXT NOT NULL REFERENCES parents,
                                       digest TEXT NOT NULL,payload TEXT NOT NULL);
            """)
            db.execute("PRAGMA foreign_keys=ON")
            db.executemany("INSERT INTO parents VALUES (?,?)", [(parent["parent_id"],
                json.dumps(parent, ensure_ascii=False)) for parent in parents])
            db.executemany("INSERT INTO fragments VALUES (?,?,?,?)", [(item["fragment"]["chunk_id"],
                item["fragment"]["parent_id"], record_digest(item), json.dumps(item, ensure_ascii=False))
                for item in records])
            db.execute("INSERT INTO manifest VALUES (1,?)", (json.dumps(manifest, ensure_ascii=False),))
        write_json(temporary / "manifest.json", manifest)
        os.rename(temporary, target)
    verify_existing(target, manifest, records, parents)
    return target, False
