"""Reutiliza únicamente vectores de una generación íntegra y del mismo bundle."""
import hashlib
import json
import sqlite3
from contextlib import closing

import numpy as np

from .common import IndexUnavailable
from .generation import verify


def active_receipt(publisher):
    try:
        return publisher.registry.active()
    except IndexUnavailable:
        return None


def verified_vectors(publisher, receipt):
    key = receipt["key"]
    if key["bundle_fingerprint"] != publisher.encoder.fingerprint:
        raise IndexUnavailable("No se comparan ni reutilizan vectores de otro bundle")
    folder = publisher.root / "generations" / key["generation_id"]
    manifest = verify(folder, receipt, publisher.owner, publisher.encoder.fingerprint)
    with closing(sqlite3.connect((folder / "catalog.sqlite3").as_uri() + "?mode=ro", uri=True)) as db:
        inputs = {}
        for chunk, payload in db.execute("SELECT chunk_id,payload FROM fragments"):
            row = json.loads(payload)
            text = row["embedding_input"]
            if hashlib.sha256(text.encode()).hexdigest() != row["embedding_input_sha256"]:
                raise IndexUnavailable("Huella de entrada E5 incoherente en la generación verificada")
            inputs[chunk] = text
    vectors = {point["id"]: np.asarray(point["vector"], dtype=np.float32)
               for point in publisher.owner.points(receipt["collection"])}
    return manifest, inputs, vectors


class ReusingEncoder:
    def __init__(self, encoder, previous):
        self.encoder = encoder
        self.previous = previous
        self.reused = self.computed = 0

    def __call__(self, inputs):
        missing = dict.fromkeys(text for text in inputs if text not in self.previous)
        generated = dict(zip(missing, self.encoder.encode_passages(list(missing)), strict=True)) if missing else {}
        self.reused = sum(text in self.previous for text in inputs)
        self.computed = len(generated)
        result = [self.previous[text] if text in self.previous else generated[text] for text in inputs]
        return np.asarray(result, dtype=np.float32).reshape(len(inputs), 384)


def compare_generations(publisher, reference, candidate):
    old, old_inputs, old_vectors = verified_vectors(publisher, reference)
    new, new_inputs, new_vectors = verified_vectors(publisher, candidate)
    shared = {chunk for chunk in old_inputs.keys() & new_inputs.keys()
              if old_inputs[chunk] == new_inputs[chunk]}
    max_delta = max((float(np.max(np.abs(old_vectors[chunk] - new_vectors[chunk]))) for chunk in shared),
                    default=None)
    if max_delta is not None and max_delta > 1e-5:
        raise IndexUnavailable("La nueva colección difiere en entradas E5 idénticas")
    return {"referencia": old.generation_id, "candidata": new.generation_id,
            "fragmentos_referencia": len(old_inputs), "fragmentos_candidata": len(new_inputs),
            "entradas_identicas": len(shared), "max_delta_vectores": max_delta,
            "ids_anadidos": len(new_inputs.keys() - old_inputs.keys()),
            "ids_retirados": len(old_inputs.keys() - new_inputs.keys())}
