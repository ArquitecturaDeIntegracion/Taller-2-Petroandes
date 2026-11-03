"""Prepara y verifica una generación completa antes de activar su puntero."""
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from petroandes.contracts.documents import Manifest
from petroandes.extract.output import write_json
from .common import IndexUnavailable, file_digest
from .projections import verify_projection, write_projections


def identity(generation, profile, revision, fingerprint):
    return {"generation_id": generation, "perfil": profile, "revision_gobierno": revision,
            "bundle_fingerprint": fingerprint}


def prepare(root, owner, encoder, records, parents, key, inputs):
    generation = key["generation_id"]
    folder = root / "generations" / generation
    if folder.exists():
        receipt = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
        if receipt["key"] != key:
            raise IndexUnavailable("Identidad de generación existente distinta")
        verify(folder, receipt, owner, encoder.fingerprint)
        return receipt, True
    folder.parent.mkdir(parents=True, exist_ok=True)
    collection = owner.create(generation, key["revision_gobierno"])
    vectors = encoder.encode_passages(inputs)
    owner.upsert(collection, records, vectors, generation, key["revision_gobierno"], encoder.fingerprint)
    ids = sorted(item["fragment"]["chunk_id"] for item in records)
    dense_hash = owner.verify(collection, ids, generation, key["revision_gobierno"], encoder.fingerprint)
    ident = identity(generation, key["perfil"], key["revision_gobierno"], encoder.fingerprint)
    with TemporaryDirectory(prefix="prepare-", dir=folder.parent) as temporary:
        temporary = Path(temporary)
        write_projections(temporary, records, parents, ident)
        manifest = Manifest(generation_id=generation, perfil=key["perfil"],
            revision_gobierno=key["revision_gobierno"], particion="structural-es-1.0.0",
            bundle="e5small-es-1.0.0", dimension=384, distancia="cosine",
            catalogo_sha256=file_digest(temporary / "catalog.sqlite3"),
            proyeccion_densa_sha256=dense_hash,
            proyeccion_lexica_sha256=file_digest(temporary / "lexical.sqlite3"), fragmentos=tuple(ids))
        write_json(temporary / "manifest.json", manifest.model_dump(mode="json"))
        receipt = {"key": key, "collection": collection,
                   "manifest_sha256": file_digest(temporary / "manifest.json")}
        write_json(temporary / "receipt.json", receipt)
        verify(temporary, receipt, owner, encoder.fingerprint)
        os.rename(temporary, folder)
    return receipt, False


def verify(folder, receipt, owner, fingerprint):
    if file_digest(folder / "manifest.json") != receipt["manifest_sha256"]:
        raise IndexUnavailable("Manifiesto de publicación alterado")
    manifest = Manifest.model_validate_json((folder / "manifest.json").read_text(encoding="utf-8"))
    key = receipt["key"]
    if (key["bundle_fingerprint"] != fingerprint or manifest.generation_id != key["generation_id"]
            or manifest.perfil != key["perfil"] or manifest.revision_gobierno != key["revision_gobierno"]):
        raise IndexUnavailable("Generación de otro perfil/revisión/bundle")
    ids = manifest.fragmentos
    ident = identity(manifest.generation_id, manifest.perfil, manifest.revision_gobierno, fingerprint)
    for name, expected in (("catalog", manifest.catalogo_sha256), ("lexical", manifest.proyeccion_lexica_sha256)):
        path = folder / f"{name}.sqlite3"
        if file_digest(path) != expected:
            raise IndexUnavailable("Proyección SQLite alterada o parcial")
        verify_projection(path, ids, ident)
    actual = owner.verify(receipt["collection"], ids, manifest.generation_id,
                          manifest.revision_gobierno, fingerprint)
    if actual != manifest.proyeccion_densa_sha256:
        raise IndexUnavailable("Proyección Qdrant alterada")
    with closing(sqlite3.connect((folder / "catalog.sqlite3").resolve().as_uri() + "?mode=ro", uri=True)) as db:
        records = {key: json.loads(payload)["fragment"]
                   for key, payload in db.execute("SELECT chunk_id,payload FROM fragments")}
    for point in owner.points(receipt["collection"]):
        if any(point["payload"].get(key) != value for key, value in records[point["id"]].items()):
            raise IndexUnavailable("Payload Qdrant distinto del fragmento publicado")
    return manifest
