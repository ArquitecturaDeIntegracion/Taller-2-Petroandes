"""Reproducción aislada con el snapshot certificado y los PDF del taller."""
import json
from contextlib import contextmanager
from datetime import datetime
from shutil import copyfile

from petroandes.catalog.api import Catalog
from petroandes.embeddings.encoder import E5Encoder
from petroandes.extract import pipeline, staging
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index import stage
from petroandes.index.publication import Publisher
from petroandes.paths import APP_ROOT
from petroandes.retrieve import Retriever


@contextmanager
def historical_workspace(tmp_path, monkeypatch):
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
    context = ServiceContext(identidad="ensayo-historico", grupos=frozenset(request["grupos"]),
                             ambito=request["ambito"], uso="evidencia_historica")
    root = tmp_path / "index"
    with Catalog.open(catalog_path, "laboratorio") as catalog:
        policy = EligibilityService(catalog, context, clock=lambda: reviewed_at)
        yield Retriever(root, policy, encoder), source


@contextmanager
def historical_lab(tmp_path, monkeypatch):
    with historical_workspace(tmp_path, monkeypatch) as (service, source):
        with Publisher(service.root, service.policy, service.encoder) as publisher:
            publication = publisher.publish(source)
        assert publication["eligible_documents"] == 12 and publication["governance_revision"] == 13
        with Publisher(service.root, service.policy, service.encoder) as publisher:
            manifest, _ = publisher.active()
        assert len(manifest.fragmentos) == publication["published_fragments"] == 58
        print(json.dumps({"ensayo": "corpus_revision_historica", "reloj_prueba": service.policy.clock().isoformat(),
                          "preparados": source.manifest["preparados"], **publication}))
        yield service, {row["fragment"]["chunk_id"]: row["fragment"] for row in source.records}
