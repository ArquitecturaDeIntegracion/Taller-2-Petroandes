"""Reproduce F3 a F5 en temporales con decisiones académicas ya registradas."""
import json
from datetime import datetime
from shutil import copyfile

from petroandes.catalog.api import Catalog
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.embeddings.encoder import E5Encoder
from petroandes.extract import pipeline, staging
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index import stage
from petroandes.index.publication import Publisher
from petroandes.paths import APP_ROOT
from petroandes.retrieve import Retriever


def test_certified_corpus_in_historical_review_context(tmp_path, monkeypatch):
    registration = APP_ROOT / "evidence/lab/20261103/registration"
    request = json.loads((APP_ROOT / "config/admin/lab-20261103/request/request.json").read_text(encoding="utf-8"))
    receipt = json.loads((registration / "summary.json").read_text(encoding="utf-8"))
    reviewed_at = datetime.fromisoformat(receipt["reviewed_at"])
    catalog_path = tmp_path / "review.sqlite3"
    copyfile(registration / "laboratorio-after.sqlite3", catalog_path)
    monkeypatch.setattr(pipeline, "profile_path", lambda _: catalog_path)
    for module in (pipeline, staging, stage):
        monkeypatch.setattr(module, "ARTIFACTS_DIR", tmp_path)
    prepared = pipeline.ingest("laboratorio", tmp_path / "f3")
    assert prepared["preparados"] == 19 and prepared["fragmentos"] == 92
    encoder = E5Encoder()
    source = stage.load_stage(tmp_path / "f3/manifest.json", encoder.tokenizer)
    context = ServiceContext(identidad="ensayo-historico-f5", grupos=frozenset(request["grupos"]),
                             ambito=request["ambito"], uso="evidencia_historica")
    root = tmp_path / "index"
    fragments = {row["fragment"]["chunk_id"]: row["fragment"] for row in source.records}
    with Catalog.open(catalog_path, "laboratorio") as catalog:
        policy = EligibilityService(catalog, context, clock=lambda: reviewed_at)
        with Publisher(root, policy, encoder) as publisher:
            publication = publisher.publish(source)
        assert publication["eligible_documents"] == 12 and publication["governance_revision"] == 13
        with Publisher(root, policy, encoder) as publisher:
            manifest, _ = publisher.active()
        assert len(manifest.fragmentos) == publication["published_fragments"]
        print(json.dumps({"ensayo": "corpus_revision_historica", "reloj_prueba": reviewed_at.isoformat(),
                          "preparados": prepared["preparados"], **publication}))
        service = Retriever(root, policy, encoder)
        for text, code, filters in (
            ("PRO-SEG-015 v1", "PRO-SEG-015", None),
            ("RES-CREG-0043-2024", "RES-CREG-0043-2024", None),
            ("P-101", "FIC-ACT-P101", {"activo": "P101"}),
            ("¿Durante cuánto tiempo se mantiene una presión por encima del umbral?",
             "PRO-OPE-012", {"tramo": "Ayacucho-Coveñas"}),
        ):
            report = service.search(SearchQuery(consulta=text, top_k=5, filtros=filters))
            assert report["resultado"]["estado"] == "recuperada", (text, report)
            trace = report["traza"]
            assert any(fragments[key]["doc_id"] == code for key in trace["seleccionados"])
            if not text.startswith("¿"):
                assert {fragments[key]["doc_id"] for key in trace["candidatos"]["exacta"]} == {code}
            print(json.dumps({"consulta": text, "documentos_por_rama": {
                branch: [fragments[key]["doc_id"] for key in ids]
                for branch, ids in (trace["candidatos"] | {"rrf": trace["seleccionados"]}).items()},
                "traza": trace}, ensure_ascii=True))
        ficha = service.obtain(FragmentQuery(doc_id="FIC-ACT-P101", version_documental="2", section_id="2"))
        assert ficha["resultado"]["estado"] == "encontrado"
        assert ficha["resultado"]["citas"][0]["version_documental"] == "2"
        old = service.obtain(FragmentQuery(doc_id="PRO-SEG-009", version_documental="1", section_id="1"))
        assert old["resultado"]["estado"] == "denegado"
        former = service.search(SearchQuery(consulta="PRO-SEG-009 v1"))
        assert former["resultado"]["motivo_abstencion"] == "evidencia_insuficiente"
        assert "densa" not in former["traza"]["tiempos_ms"] and "lexica" not in former["traza"]["tiempos_ms"]
