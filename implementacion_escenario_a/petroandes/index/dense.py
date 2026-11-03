"""Único propietario Qdrant local; filtros explícitos y huella lógica verificable."""
from uuid import uuid4

import numpy as np
from qdrant_client import QdrantClient, models
from petroandes.embeddings.encoder import BundleMismatch, validate_vectors
from .common import IndexUnavailable, digest


class DenseOwner:
    def __init__(self, path):
        self.client = QdrantClient(path=str(path))

    def create(self, generation, revision):
        name = f"e5small_es_1_0_0_r{revision}_{generation.replace('-', '')[:12]}_{uuid4().hex[:8]}"
        self.client.create_collection(name, vectors_config=models.VectorParams(size=384,
                                                                              distance=models.Distance.COSINE))
        return name

    def upsert(self, collection, records, vectors, generation, revision, fingerprint):
        vectors = validate_vectors(vectors, len(records))
        for offset in range(0, len(records), 16):
            points = []
            for record, vector in zip(records[offset:offset + 16], vectors[offset:offset + 16]):
                fragment = record["fragment"]
                payload = {**fragment, "generation_id": generation, "governance_revision": revision,
                    "bundle_fingerprint": fingerprint,
                    "tipo": record["metadata"]["documento"]["tipo"], "contenido_no_confiable": True}
                points.append(models.PointStruct(id=fragment["chunk_id"], vector=vector.tolist(), payload=payload))
            self.client.upsert(collection, points=points, wait=True)

    def points(self, collection):
        rows, offset = [], None
        while True:
            points, offset = self.client.scroll(collection, limit=128, offset=offset,
                                                with_payload=True, with_vectors=True)
            for point in points:
                vector = validate_vectors(np.asarray([point.vector]), 1)[0]
                rows.append({"id": str(point.id), "vector": vector.tolist(), "payload": point.payload})
            if offset is None:
                break
        return sorted(rows, key=lambda row: row["id"])

    def verify(self, collection, ids, generation, revision, fingerprint):
        info = self.client.get_collection(collection)
        if info.config.params.vectors.size != 384 or info.config.params.vectors.distance != models.Distance.COSINE:
            raise IndexUnavailable("Esquema vectorial incompatible")
        points = self.points(collection)
        if {point["id"] for point in points} != set(ids) or len(points) != len(ids):
            raise IndexUnavailable("Cardinalidad o identidades densas incoherentes")
        for point in points:
            payload = point["payload"]
            if (payload.get("generation_id") != generation or payload.get("governance_revision") != revision
                    or payload.get("bundle_fingerprint") != fingerprint or payload.get("chunk_id") != point["id"]):
                raise IndexUnavailable("Payload vectorial de otra generación/revisión/bundle")
        return digest(points)

    def search(self, collection, query, eligible_ids, *, generation, revision, fingerprint, limit=5):
        if query.bundle_fingerprint != fingerprint:
            raise BundleMismatch("Vector de pregunta e índice de bundles distintos")
        validate_vectors(np.asarray([query.vector]), 1)
        if not eligible_ids:
            return []
        query_filter = models.Filter(must=[models.HasIdCondition(has_id=sorted(eligible_ids)),
            models.FieldCondition(key="generation_id", match=models.MatchValue(value=generation)),
            models.FieldCondition(key="governance_revision", match=models.MatchValue(value=revision)),
            models.FieldCondition(key="bundle_fingerprint", match=models.MatchValue(value=fingerprint))])
        return self.client.query_points(collection, query=query.vector.tolist(), query_filter=query_filter,
                                        limit=limit).points

    def close(self):
        self.client.close()
