"""Sonda Qdrant local, filtro previo, reapertura, bloqueo y SQLite real."""
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory


def probe():
    from pydantic import BaseModel, ValidationError
    from qdrant_client import QdrantClient, models
    from rank_bm25 import BM25Okapi

    class Row(BaseModel):
        revision: int

    try:
        Row(revision="no-es-entero")
    except ValidationError:
        pass
    else:
        raise AssertionError("Pydantic aceptó una revisión inválida")
    with TemporaryDirectory(prefix="f0-qdrant-") as temp:
        path = str(Path(temp) / "qdrant")
        client = QdrantClient(path=path)
        try:
            client.create_collection("f0", vectors_config=models.VectorParams(
                size=4, distance=models.Distance.COSINE))
            client.upsert("f0", points=[
                models.PointStruct(id=1, vector=[0.8, 0.6, 0.0, 0.0],
                                   payload={"revision": 7}),
                models.PointStruct(id=2, vector=[1.0, 0.0, 0.0, 0.0],
                                   payload={"revision": 7}),
                models.PointStruct(id=3, vector=[1.0, 0.0, 0.0, 0.0],
                                   payload={"revision": 6})])
            query_filter = models.Filter(must=[models.HasIdCondition(has_id=[1, 3]),
                models.FieldCondition(key="revision", match=models.MatchValue(value=7))])
            query = dict(collection_name="f0", query=[1.0, 0.0, 0.0, 0.0],
                         query_filter=query_filter, limit=5)
            before = [p.id for p in client.query_points(**query).points]
            assert before == [1], before
            script = (
                "import sys\nfrom qdrant_client import QdrantClient\n"
                "try:\n c=QdrantClient(path=sys.argv[1])\n"
                "except RuntimeError as e:\n print(str(e)); sys.exit(23)\n"
                "else:\n c.close(); sys.exit(0)\n")
            lock = subprocess.run([sys.executable, "-c", script, path],
                                  capture_output=True, text=True, timeout=45)
            assert lock.returncode == 23 and "already accessed" in lock.stdout, lock
        finally:
            client.close()
        client = QdrantClient(path=path)
        try:
            after = [p.id for p in client.query_points(**query).points]
            assert after == before
            assert client.count("f0", exact=True).count == 3
        finally:
            client.close()
        database = Path(temp) / "catalog.sqlite"
        with closing(sqlite3.connect(database)) as db, db:
            db.execute("CREATE TABLE revisions (revision INTEGER PRIMARY KEY)")
            db.execute("INSERT INTO revisions VALUES (?)", (7,))
        with closing(sqlite3.connect(database)) as db, db:
            assert db.execute("SELECT revision FROM revisions").fetchall() == [(7,)]
            db.execute("INSERT INTO revisions VALUES (?)", (8,))
            db.rollback()
            assert db.execute("SELECT revision FROM revisions").fetchall() == [(7,)]
    lexical = BM25Okapi([["manual", "p-101"], ["alarma", "tramo"], ["sin", "datos"]])
    assert int(lexical.get_scores(["p-101"]).argmax()) == 0
    return {"status": "passed", "qdrant_mode": "local_persistent", "server_used": False,
            "inserted_ids": [1, 2, 3], "eligible_ids": [1, 3], "revision": 7,
            "filtered_ids": before, "reopened_ids": after,
            "closer_ineligible_and_stale_vectors_excluded": True,
            "second_owner_exit_code": lock.returncode,
            "second_owner_message": lock.stdout.strip(),
            "sqlite_version": sqlite3.sqlite_version, "sqlite_rollback": "passed",
            "pydantic_invalid_input": "rejected", "bm25_exact_token": "passed",
            "scope": "Compatibilidad sintética, no certifica gobierno del corpus"}
