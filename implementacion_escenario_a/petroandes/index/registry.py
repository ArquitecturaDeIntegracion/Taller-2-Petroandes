"""Puntero activo transaccional; solo acepta generaciones ya verificadas."""
import json
import sqlite3

from .common import IndexUnavailable


class Registry:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS generations(id TEXT PRIMARY KEY,receipt TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS active(singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                generation TEXT NOT NULL REFERENCES generations(id));
        """)
        self.db.execute("PRAGMA foreign_keys=ON")

    def activate(self, generation, receipt):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            encoded = json.dumps(receipt, sort_keys=True)
            existing = self.db.execute("SELECT receipt FROM generations WHERE id=?", (generation,)).fetchone()
            if existing and existing[0] != encoded:
                raise IndexUnavailable("Generación registrada con otra identidad")
            self.db.execute("INSERT OR IGNORE INTO generations VALUES (?,?)", (generation, encoded))
            self.db.execute("INSERT INTO active VALUES (1,?) ON CONFLICT(singleton) DO UPDATE SET generation=?",
                            (generation, generation))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def active(self):
        row = self.db.execute("SELECT receipt FROM generations JOIN active ON id=generation").fetchone()
        if not row:
            raise IndexUnavailable("No hay generación activa")
        return json.loads(row[0])

    def close(self):
        self.db.close()
