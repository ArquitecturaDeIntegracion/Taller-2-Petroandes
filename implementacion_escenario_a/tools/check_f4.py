"""Cierre técnico F4 con reapertura real, archivos exportados y auditoría intacta."""
import argparse
import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

import numpy as np
from petroandes.catalog.api import Catalog
from petroandes.catalog.store import index_directory, profile_path
from petroandes.embeddings.encoder import E5Encoder, validate_vectors
from petroandes.extract.output import write_json
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index.common import file_digest
from petroandes.index.publication import Publisher
from petroandes.paths import APP_ROOT
from f0_common import configure_cache


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    configure_cache(offline=True)
    encoder = E5Encoder()
    audit = json.loads((args.audit / "summary.json").read_text())
    for name, expected in audit["sha256"].items():
        assert file_digest(args.audit / name) == expected
    vectors = np.load(args.audit / "vectors.npy", allow_pickle=False)
    validate_vectors(vectors, audit["count"])
    assert audit["count"] == 92
    bundle = json.loads((args.audit / "bundle.json").read_text())
    assert bundle["fingerprint"] == encoder.fingerprint
    context = ServiceContext.model_validate_json((APP_ROOT / "config/f4-context.json").read_text())
    profiles = []
    for profile in ("baseline", "laboratorio"):
        root = index_directory(profile)
        with Catalog.open(profile_path(profile), profile) as catalog:
            before = catalog.summary()
            policy = EligibilityService(catalog, context)
            with Publisher(root, policy, encoder) as publisher:
                manifest, receipt = publisher.active()
                assert manifest.fragmentos == () and policy.eligible().documentos == ()
                assert before["clasificacion"] == {"pendiente": 15, "excluido": 4, "certificado": 0}
                assert before["decisiones_registradas"] == 0 and before["governance_revision"] == 1
                assert publisher.owner.client.count(receipt["collection"], exact=True).count == 0
            # Copias de generaciones inmutables con cliente Qdrant ya cerrado.
            exported = destination / profile
            exported.mkdir()
            source = root / "generations" / manifest.generation_id
            for name in ("manifest.json", "receipt.json", "catalog.sqlite3", "lexical.sqlite3"):
                shutil.copyfile(source / name, exported / name)
            with closing(sqlite3.connect(root / "publications.sqlite3")) as registry:
                with closing(sqlite3.connect(exported / "publications.sqlite3")) as backup:
                    registry.backup(backup)
            with closing(sqlite3.connect(exported / "catalog.sqlite3")) as db:
                assert db.execute("SELECT count(*) FROM fragments").fetchone()[0] == 0
            assert catalog.summary() == before
            profiles.append({"perfil": profile, "generation_id": manifest.generation_id,
                "revision_gobierno": manifest.revision_gobierno, "published_fragments": 0,
                "dense_points": 0, "catalog_summary": before,
                "exported_sha256": {path.name: file_digest(path) for path in sorted(exported.iterdir())}})
    report = {"status": "passed", "scope": "F4 técnica; no certificaciones ni herramientas finales",
        "audit_vectors": audit["count"], "bundle_fingerprint": encoder.fingerprint,
        "profiles": profiles, "academic_review_pending": True,
        "reconstruction": "Reingerir PDF y publicar; no usar snapshots nativos Qdrant local"}
    write_json(destination / "closure.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
