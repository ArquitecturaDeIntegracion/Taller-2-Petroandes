import json
import sqlite3
from contextlib import closing
from datetime import timedelta

import pytest
from qdrant_client import QdrantClient, models

from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.embeddings.encoder import E5Encoder
from petroandes.governance.eligibility import EligibilityService
from petroandes.index.dense import DenseOwner
from petroandes.index.projections import lexical_search
from petroandes.index.publication import Publisher
from petroandes.retrieve import Retriever
from f2_helpers import NOW, catalog, context, record
from f5_helpers import fixture_stage, trace


@pytest.fixture(scope="module")
def encoder():
    return E5Encoder()


@pytest.fixture
def lab(tmp_path, encoder):
    with catalog(tmp_path) as store:
        stage, documents = fixture_stage(store, encoder)
        instant = [NOW]
        policy = EligibilityService(store, context(), clock=lambda: instant[0])
        root = tmp_path / "index"
        with Publisher(root, policy, encoder) as publisher:
            publication = publisher.publish(stage)
        yield store, policy, root, Retriever(root, policy, encoder), stage, documents, instant, publication


def query(text, **kwargs):
    return SearchQuery(consulta=text, **kwargs)


def reference(code, version, section="ficha", **kwargs):
    return FragmentQuery(doc_id=code, version_documental=version, section_id=section, **kwargs)


@pytest.mark.parametrize("text,code,version", [
    ("PRO-SEG-015 versión v1", "PRO-SEG-015", "v1"),
    ("RES-CREG-0043-2024", "RES-CREG-0043-2024", None),
    ("bomba P-101", "FIC-ACT-P101", "v2"),
    ("bomba P101", "FIC-ACT-P101", "v2"),
])
def test_exact_codes_and_versions(lab, text, code, version):
    _, _, _, service, stage, *_ = lab
    expected = {row["fragment"]["chunk_id"] for row in stage.records
                if (row["fragment"]["doc_id"], row["fragment"]["version_documental"]) == (code, version)}
    report = service.search(query(text, top_k=1))
    branches = report["traza"]["candidatos"]
    assert set(branches["exacta"]) == expected
    assert branches["lexica"][0] in expected
    assert report["resultado"]["evidencia"][0]["chunk_id"] in expected
    if report["traza"]["modo"] == "codigo_exacto":
        assert all(set(ids) <= expected for ids in branches.values())
    trace(report)


def test_paraphrase_and_context(lab):
    _, _, _, service, *_ = lab
    report = service.search(query("¿Cómo interrumpir el flujo ante un escape?", top_k=3,
                                  filtros={"tipo": "procedimiento", "tramo": "tramo-sintetico"}))
    branches = report["traza"]["candidatos"]
    evidence = report["resultado"]["evidencia"]
    assert not branches["exacta"] and len(evidence) == len({row["chunk_id"] for row in evidence}) == 3
    assert any(row["doc_id"] == "PRO-SEG-015" and row["section_id"] == "secuencia" for row in evidence)
    anchor = service.obtain(reference("PRO-SEG-015", "v1", "secuencia", parte=2))
    part = anchor["resultado"]["partes"][0]
    assert part["parte"] == 2
    expanded = service.expand(part["chunk_id"])
    assert [row["section_id"] for row in expanded["resultado"]["partes"]] == [
        "requisitos", "secuencia", "secuencia"]
    assert len(expanded["resultado"]["citas"]) == 3
    trace(report)
    trace(anchor)
    trace(expanded)


def test_expired_point_is_competitive_but_filtered(lab, encoder, monkeypatch):
    _, _, root, service, stage, _, instant, publication = lab
    old = next(row["fragment"] for row in stage.records if row["fragment"]["doc_id"] == "PRO-SEG-009")
    old_id = old["chunk_id"]
    raw_vector = encoder.query("Válvula violeta. Bloqueo del paso tras una pérdida de contención.",
                               expected_fingerprint=encoder.fingerprint)
    collection = publication["collection"]
    folder = root / "generations" / publication["generation_id"]
    instant[0] += timedelta(hours=1)
    with closing(DenseOwner(root / "qdrant")) as owner:
        assert owner.client.retrieve(collection, [old_id], with_vectors=True)[0].vector
        unfiltered = owner.client.query_points(collection, query=raw_vector.vector.tolist(), limit=1).points
        assert str(unfiltered[0].id) == old_id
    all_ids = {row["fragment"]["chunk_id"] for row in stage.records}
    assert lexical_search(folder / "lexical.sqlite3", "válvula violeta", all_ids)[0][0] == old_id

    actual = QdrantClient.query_points
    calls = []

    def inspect(client, name, **kwargs):
        calls.append(kwargs["query_filter"])
        return actual(client, name, **kwargs)

    monkeypatch.setattr(QdrantClient, "query_points", inspect)
    report = service.search(query("PRO-SEG-009 válvula violeta"))
    assert len(calls) == 1
    conditions = calls[0].must
    assert isinstance(conditions[0], models.HasIdCondition)
    assert set(conditions[0].has_id) == all_ids - {old_id}
    assert {condition.key: condition.match.value for condition in conditions[1:]} == {
        "generation_id": publication["generation_id"], "governance_revision": publication["governance_revision"],
        "bundle_fingerprint": encoder.fingerprint}
    assert all(old_id not in ids for ids in report["traza"]["candidatos"].values())
    assert old_id not in report["traza"]["seleccionados"]
    assert service.obtain(reference("PRO-SEG-009", "v1"))["resultado"]["estado"] == "denegado"
    assert service.expand(old_id)["resultado"]["estado"] == "denegado"
    print(json.dumps({"competidor_fisico": old_id, "prefiltro_qdrant": calls[0].model_dump(mode="json")}))
    trace(report)


def test_revocation_during_search_preserves_points_and_denies_every_route(lab, encoder, monkeypatch):
    store, _, root, service, stage, documents, _, publication = lab
    old = documents["PRO-SEG-009", "v1"]
    chunk_id = next(row["fragment"]["chunk_id"] for row in stage.records
                    if row["fragment"]["doc_id"] == old.doc_id)
    request = query("PRO-SEG-009 válvula violeta")
    assert service.search(request)["traza"]["seleccionados"][0] == chunk_id
    before = store.verify_revision()
    original = QdrantClient.query_points

    def revoke(client, collection, **kwargs):
        points = original(client, collection, **kwargs)
        store.apply_decision(record(old, before + 1, estado="excluido"), before)
        return points

    with monkeypatch.context() as patch:
        patch.setattr(QdrantClient, "query_points", revoke)
        raced = service.search(request)
    assert raced["resultado"]["motivo_abstencion"] == "gobierno_cambio"
    assert "candidatos" not in raced["traza"] and "evidencia" not in raced["resultado"]
    assert store.verify_revision() == before + 1
    with closing(DenseOwner(root / "qdrant")) as owner:
        assert owner.client.retrieve(publication["collection"], [chunk_id], with_vectors=True)[0].vector
        raw = original(owner.client, publication["collection"], query=encoder.query(request.consulta,
            expected_fingerprint=encoder.fingerprint).vector.tolist(), limit=1)
        assert str(raw.points[0].id) == chunk_id
    folder = root / "generations" / publication["generation_id"]
    with closing(sqlite3.connect(folder / "lexical.sqlite3")) as db:
        assert "violeta" in json.loads(db.execute("SELECT payload FROM fragments WHERE chunk_id=?",
                                                 (chunk_id,)).fetchone()[0])
    blocked = service.search(request)
    assert blocked["resultado"]["motivo_abstencion"] == "gobierno_cambio"
    assert not {"densa", "lexica", "exacta"}.intersection(blocked["traza"]["tiempos_ms"])
    assert service.obtain(reference(old.doc_id, "v1"))["resultado"]["estado"] == "denegado"
    assert service.expand(chunk_id)["resultado"]["estado"] == "denegado"
    trace(raced)
    trace(blocked)


def test_empty_filters_missing_index_and_excessive_query(lab, encoder, monkeypatch, tmp_path):
    store, policy, root, service, *_ = lab
    assert service.search(query("bomba", filtros={"activo": "P-999"}))["resultado"][
        "motivo_abstencion"] == "sin_evidencia_autorizada"
    assert service.search(query("1 " * 600))["traza"]["entrada_e5_excedida"]
    assert Retriever(tmp_path / "absent", policy, encoder).search(query("bomba"))["resultado"][
        "error"] == "indice_no_listo"
    assert not (tmp_path / "absent").exists()
    empty = EligibilityService(store, context(grupos=frozenset({"OTRO"})), clock=lambda: NOW)
    monkeypatch.setattr(QdrantClient, "query_points", lambda *_a, **_k: pytest.fail("Qdrant llamado sin permisos"))
    result = Retriever(root, empty, encoder).search(query("P-101"))
    assert result["resultado"]["motivo_abstencion"] == "sin_evidencia_autorizada"
    assert not {"embedding", "generacion", "lexica"}.intersection(result["traza"]["tiempos_ms"])
