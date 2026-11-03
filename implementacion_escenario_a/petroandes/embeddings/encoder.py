"""Adaptador E5 real: revisión/artefactos fijados, media enmascarada, L2 y CPU."""
import hashlib
import importlib.metadata
import json
from dataclasses import dataclass
from time import perf_counter

import numpy as np
from petroandes.paths import APP_ROOT, MODELS_DIR
from .input import E5Tokenizer


class BundleMismatch(ValueError):
    pass


@dataclass(frozen=True)
class EncodedQuery:
    bundle_fingerprint: str
    vector: np.ndarray


def validate_vectors(vectors, count, dimension=384):
    vectors = np.asarray(vectors, dtype=np.float32)
    if vectors.shape != (count, dimension) or not np.isfinite(vectors).all():
        raise ValueError("Dimensión, cardinalidad o valores de vectores inválidos")
    if count and not np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5):
        raise ValueError("Vectores sin normalización L2")
    return vectors


class E5Encoder:
    def __init__(self, *, batch_size=4, threads=2):
        import torch
        from sentence_transformers import SentenceTransformer

        if type(batch_size) is not int or not 1 <= batch_size <= 8:
            raise ValueError("Lote CPU debe ser entero entre 1 y 8")
        start = perf_counter()
        self.tokenizer = E5Tokenizer()
        self.config = self.tokenizer.config
        fixed = {"bundle": "e5small-es-1.0.0", "model": "intfloat/multilingual-e5-small",
                 "dimension": 384, "distance": "cosine", "max_input_tokens": 448}
        if any(self.config.get(key) != value for key, value in fixed.items()):
            raise BundleMismatch("Configuración distinta del contrato E5 fijado")
        expected = json.loads((APP_ROOT / "config/e5-artifacts.json").read_text(encoding="utf-8"))
        if expected["revision"] != self.config["revision"]:
            raise BundleMismatch("Revisiones de modelo y tokenizador distintas")
        folder = MODELS_DIR / ("e5-" + self.config["revision"])
        observed = {}
        for name, digest in expected["sha256"].items():
            hasher = hashlib.sha256()
            with (folder / name).open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    hasher.update(block)
            observed[name] = hasher.hexdigest()
            if observed[name] != digest:
                raise BundleMismatch(f"Artefacto E5 distinto de la revisión fijada: {name}")
        torch.set_num_threads(threads)
        self.model = SentenceTransformer(str(folder), device="cpu", local_files_only=True,
                                         trust_remote_code=False)
        self.model.max_seq_length = 448
        self.batch_size = batch_size
        self.receipt = {"bundle": self.config["bundle"], "model": self.config["model"],
            "revision": self.config["revision"], "tokenizer_revision": self.config["revision"],
            "dimension": 384, "distance": "cosine", "pooling": "masked_mean", "normalization": "L2",
            "prefixes": ["query:", "passage:"], "max_input_tokens": 448,
            "artifacts_sha256": observed, "libraries": {name: importlib.metadata.version(name)
                for name in ("torch", "sentence-transformers", "transformers", "numpy")}}
        encoded = json.dumps(self.receipt, sort_keys=True, ensure_ascii=False).encode()
        self.fingerprint = hashlib.sha256(encoded).hexdigest()
        self.load_seconds = perf_counter() - start
        self.batches = []
        self.manual_pooling_delta = self.check_pooling()

    def encode_passages(self, inputs):
        return self._encode(inputs, "passage: ")

    def _encode(self, inputs, prefix):
        import psutil

        if any(not text.startswith(prefix) for text in inputs):
            raise ValueError("Prefijo incorrecto para el tipo de entrada E5")
        if any(self.tokenizer.count(text) > 448 for text in inputs):
            raise ValueError("Entrada E5 excedida; no truncar")
        parts = []
        for index in range(0, len(inputs), self.batch_size):
            batch = inputs[index:index + self.batch_size]
            start = perf_counter()
            vectors = self.model.encode(batch, batch_size=self.batch_size, normalize_embeddings=True,
                                        show_progress_bar=False, convert_to_numpy=True)
            parts.append(validate_vectors(vectors, len(batch)))
            self.batches.append({"count": len(batch), "seconds": perf_counter() - start,
                                 "rss_bytes": psutil.Process().memory_info().rss})
        result = np.concatenate(parts) if parts else np.empty((0, 384), dtype=np.float32)
        return validate_vectors(result, len(inputs))

    def query(self, text, *, expected_fingerprint):
        if expected_fingerprint != self.fingerprint:
            raise BundleMismatch("Pregunta e índice no comparten bundle efectivo")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Pregunta vacía")
        return EncodedQuery(self.fingerprint, self._encode(["query: " + text.strip()], "query: ")[0])

    def check_pooling(self):
        import torch

        texts = ["query: ¿Qué registra la ficha sintética?", "passage: La ficha sintética registra una revisión."]
        actual = self._encode(texts[:1], "query: ")
        actual = np.concatenate([actual, self.encode_passages(texts[1:])])
        batch = self.model.tokenizer(texts, padding=True, truncation=False, return_tensors="pt")
        with torch.inference_mode():
            output = self.model[0].auto_model(**batch).last_hidden_state
            mask = batch["attention_mask"].unsqueeze(-1).to(output.dtype)
            manual = torch.nn.functional.normalize((output * mask).sum(1) / mask.sum(1), dim=1).numpy()
        delta = float(np.max(np.abs(actual - manual)))
        if delta >= 1e-5:
            raise BundleMismatch("Adaptador real no coincide con media enmascarada y L2")
        return delta
