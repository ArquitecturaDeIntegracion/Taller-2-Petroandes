"""Conexiones, revisión y outbox transaccionales; abrir nunca crea un catálogo vacío."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from petroandes.paths import ARTIFACTS_DIR
from .schema import SCHEMA, SCHEMA_VERSION


class CatalogUnavailable(RuntimeError):
    pass


class RevisionConflict(RuntimeError):
    pass


def document_key(reference):
    encoded = json.dumps([reference.doc_id, reference.version_documental], ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def profile_path(perfil):
    if perfil not in ("baseline", "laboratorio"):
        raise ValueError("Perfil de gobierno desconocido")
    return ARTIFACTS_DIR / "catalog" / perfil / "catalog.sqlite3"


def index_directory(perfil):
    profile_path(perfil)
    return ARTIFACTS_DIR / "indexes" / perfil


class Store:
    def __init__(self, connection, perfil):
        self.db = connection
        self.perfil = perfil
        self.db.execute("PRAGMA foreign_keys = ON")
        self.verify_revision()

    @classmethod
    def create(cls, path, perfil):
        profile_path(perfil)
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb"):
            pass
        connection = sqlite3.connect(path, isolation_level=None)
        try:
            connection.executescript(SCHEMA)
            connection.execute("INSERT INTO metadata VALUES (1, ?, ?, 0)",
                               (SCHEMA_VERSION, perfil))
            return cls(connection, perfil)
        except Exception:
            connection.close()
            raise

    @classmethod
    def open(cls, path, perfil, *, read_only=False):
        profile_path(perfil)
        try:
            mode = "ro" if read_only else "rw"
            connection = sqlite3.connect(Path(path).resolve().as_uri() + f"?mode={mode}",
                                         uri=True, isolation_level=None)
            try:
                return cls(connection, perfil)
            except Exception:
                connection.close()
                raise
        except (sqlite3.Error, ValueError) as exc:
            raise CatalogUnavailable("Catálogo ausente, inválido o inaccesible") from exc

    def verify_revision(self):
        try:
            rows = self.db.execute("SELECT schema_version, perfil, revision FROM metadata").fetchall()
            if len(rows) != 1:
                raise CatalogUnavailable("Metadatos de gobierno incoherentes")
            schema, perfil, revision = rows[0]
            count, last = self.db.execute("SELECT count(*), coalesce(max(revision),0) FROM events").fetchone()
            if (schema != SCHEMA_VERSION or perfil != self.perfil or revision != count
                    or revision != last or self.db.execute("PRAGMA user_version").fetchone()[0] != schema):
                raise CatalogUnavailable("Perfil, migración o revisión incoherente")
            return revision
        except sqlite3.Error as exc:
            raise CatalogUnavailable("No se puede confirmar la revisión de gobierno") from exc

    def change(self, expected_revision, kind, payload, mutation):
        owns_transaction = not self.db.in_transaction
        if owns_transaction:
            self.db.execute("BEGIN IMMEDIATE")
        try:
            current = self.verify_revision()
            if type(expected_revision) is not int or current != expected_revision:
                raise RevisionConflict("La revisión de gobierno cambió; recargar antes de escribir")
            revision = current + 1
            if not mutation(revision):
                if owns_transaction:
                    self.db.rollback()
                return current
            self.db.execute("INSERT INTO events (revision,event_id,kind,payload,recorded_at) VALUES (?,?,?,?,?)",
                (revision, str(uuid4()), kind, json.dumps(payload, ensure_ascii=False),
                 datetime.now(timezone.utc).isoformat()))
            self.db.execute("UPDATE metadata SET revision=? WHERE singleton=1", (revision,))
            if owns_transaction:
                self.db.commit()
            return revision
        except Exception:
            if owns_transaction:
                self.db.rollback()
            raise

    def pending_events(self):
        self.verify_revision()
        return self.db.execute("SELECT revision,kind,payload FROM events WHERE pending=1 ORDER BY revision").fetchall()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
