"""Proyecciones SQLite de lectura; BM25 se construye solo sobre IDs elegibles."""
import json
import re
import sqlite3
from contextlib import closing

from rank_bm25 import BM25Okapi
from .common import IndexUnavailable

LEXICAL_VERSION = "bm25-codes-es-1.0.0"


def tokens(text):
    # Mantiene códigos enteros, guiones y años. Las palabras usan Unicode.
    return re.findall(r"[^\W_]+(?:[-./][^\W_]+)*", text.casefold(), re.UNICODE)


def write_projections(folder, records, parents, identity):
    parent_ids = {item["fragment"]["parent_id"] for item in records}
    for name in ("catalog", "lexical"):
        with closing(sqlite3.connect(folder / f"{name}.sqlite3")) as db, db:
            db.execute("CREATE TABLE metadata(payload TEXT NOT NULL)")
            db.execute("INSERT INTO metadata VALUES (?)", (json.dumps(identity, sort_keys=True),))
            db.execute("CREATE TABLE fragments(chunk_id TEXT PRIMARY KEY,payload TEXT NOT NULL)")
            if name == "catalog":
                db.execute("CREATE TABLE parents(parent_id TEXT PRIMARY KEY,payload TEXT NOT NULL)")
                db.executemany("INSERT INTO parents VALUES (?,?)", [(item["parent_id"], json.dumps(item))
                    for item in parents if item["parent_id"] in parent_ids])
            for item in records:
                fragment = item["fragment"]
                metadata = dict(item["metadata"])
                metadata["gobierno_en_ingesta"] = metadata.pop("gobierno", None)
                metadata["gobierno"] = {"governance_revision": identity["revision_gobierno"],
                    "perfil": identity["perfil"], "fuente": "registro_externo_no_autoriza_por_payload"}
                metadata["publicacion"] = identity
                metadata["publication_state"] = "publicado_para_contexto"
                value = item | {"metadata": metadata} if name == "catalog" else tokens(item["embedding_input"])
                db.execute("INSERT INTO fragments VALUES (?,?)", (fragment["chunk_id"], json.dumps(value)))


def verify_projection(path, ids, identity):
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        rows = db.execute("SELECT payload FROM metadata").fetchall()
        actual = {row[0] for row in db.execute("SELECT chunk_id FROM fragments")}
        if rows != [(json.dumps(identity, sort_keys=True),)] or actual != set(ids):
            raise IndexUnavailable("Proyección parcial o de otra revisión")
        if path.name == "catalog.sqlite3":
            from petroandes.contracts.documents import Fragment

            parent_ids = {row[0] for row in db.execute("SELECT parent_id FROM parents")}
            used = set()
            for key, payload in db.execute("SELECT chunk_id,payload FROM fragments"):
                item = json.loads(payload)
                fragment = Fragment.model_validate(item["fragment"])
                if (fragment.chunk_id != key or fragment.parent_id not in parent_ids
                        or item["metadata"]["publicacion"] != identity
                        or item["metadata"]["gobierno"]["governance_revision"] != identity["revision_gobierno"]):
                    raise IndexUnavailable("Fragmentos publicados incoherentes")
                used.add(fragment.parent_id)
            if used != parent_ids:
                raise IndexUnavailable("Padres ajenos al subconjunto publicado")


def lexical_search(path, text, eligible_ids, limit=5):
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        rows = [(key, json.loads(payload)) for key, payload in db.execute(
            "SELECT chunk_id,payload FROM fragments ORDER BY chunk_id") if key in eligible_ids]
    if not rows:
        return []
    query = tokens(text)
    scores = BM25Okapi([row[1] for row in rows]).get_scores(query)
    hits = [(key, float(score)) for (key, words), score in zip(rows, scores) if set(query).intersection(words)]
    return sorted(hits, key=lambda row: (-row[1], row[0]))[:limit]
