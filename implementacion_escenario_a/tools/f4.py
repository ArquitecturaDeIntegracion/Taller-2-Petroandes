"""Embeddings de auditoría y publicación gobernada local; sin decisiones implícitas."""
import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from petroandes.catalog.api import Catalog
from petroandes.catalog.store import index_directory, profile_path
from petroandes.embeddings.encoder import E5Encoder, validate_vectors
from petroandes.extract.output import write_json
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index.common import file_digest
from petroandes.index.publication import Publisher
from petroandes.index.stage import load_stage
from petroandes.paths import APP_ROOT, ARTIFACTS_DIR
from f0_common import configure_cache, memory


def audit(stage, encoder, destination):
    destination.mkdir(parents=True, exist_ok=False)
    start = perf_counter()
    first_batch = len(encoder.batches)
    vectors = encoder.encode_passages([item["embedding_input"] for item in stage.records])
    np.save(destination / "vectors.npy", vectors, allow_pickle=False)
    reloaded = np.load(destination / "vectors.npy", allow_pickle=False)
    validate_vectors(reloaded, len(stage.records))
    assert np.array_equal(vectors, reloaded)
    with (destination / "rows.jsonl").open("w", encoding="utf-8") as output:
        for row, item in enumerate(stage.records):
            output.write(json.dumps({"row": row, "chunk_id": item["fragment"]["chunk_id"],
                "input_sha256": item["embedding_input_sha256"]}) + "\n")
    write_json(destination / "bundle.json", {"fingerprint": encoder.fingerprint, **encoder.receipt})
    write_json(destination / "batches.json", encoder.batches[first_batch:])
    norms = np.linalg.norm(vectors, axis=1)
    report = {"purpose": "auditoria_no_consultable_no_autoriza_corpus", "stage": stage.manifest["generation_id"],
        "count": len(vectors), "dimension": 384, "finite": bool(np.isfinite(vectors).all()),
        "norm_min": float(norms.min()), "norm_max": float(norms.max()), "batch_size": encoder.batch_size,
        "encoding_seconds": perf_counter() - start, "model_load_seconds": encoder.load_seconds,
        "manual_pooling_max_delta": encoder.manual_pooling_delta, "memory": memory(),
        "sha256": {name: file_digest(destination / name)
                   for name in ("vectors.npy", "rows.jsonl", "bundle.json", "batches.json")}}
    write_json(destination / "summary.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "publish", "inspect"))
    parser.add_argument("--profile", choices=("baseline", "laboratorio"), default="baseline")
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    configure_cache(offline=True)
    encoder = E5Encoder()
    if args.action == "audit":
        if not args.stage:
            parser.error("audit requiere --stage")
        report = audit(load_stage(args.stage.resolve(), encoder.tokenizer), encoder, args.output.resolve())
    else:
        context = ServiceContext.model_validate_json((APP_ROOT / "config/f4-context.json").read_text())
        with Catalog.open(profile_path(args.profile), args.profile) as catalog:
            policy = EligibilityService(catalog, context)
            with Publisher(index_directory(args.profile), policy, encoder) as publisher:
                if args.action == "publish":
                    if not args.stage:
                        parser.error("publish requiere --stage")
                    report = publisher.publish(load_stage(args.stage.resolve(), encoder.tokenizer))
                else:
                    manifest, receipt = publisher.active()
                    report = {"manifest": manifest.model_dump(mode="json"), "receipt": receipt}
                report["catalog_summary"] = catalog.summary()
                report["index_ref"] = {"base": "artifacts", "path": index_directory(
                    args.profile).relative_to(ARTIFACTS_DIR).as_posix()}
                write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
