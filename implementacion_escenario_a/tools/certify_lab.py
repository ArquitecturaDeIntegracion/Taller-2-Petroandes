"""Registro administrativo acotado: copia antes/después y decisiones individuales."""
import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path
from petroandes.extract.output import write_json, write_jsonl
from petroandes.governance.administration import load_request, request_digest
from petroandes.governance.registration import register
from petroandes.index.common import file_digest


def backup(catalog, path):
    with closing(sqlite3.connect(path)) as copy:
        catalog.db.backup(copy)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    request = load_request(args.request.resolve())
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    baseline = profile_path("baseline")
    before_hash = file_digest(baseline)
    with Catalog.open(baseline, "baseline", read_only=True) as base:
        baseline_summary = base.summary()
        backup(base, destination / "baseline-before.sqlite3")
    with Catalog.open(profile_path("laboratorio"), "laboratorio") as catalog:
        before = catalog.summary()
        backup(catalog, destination / "laboratorio-before.sqlite3")
        records, reused = register(catalog, request)
        after = catalog.summary()
        backup(catalog, destination / "laboratorio-after.sqlite3")
        (destination / "decisions").mkdir()
        for number, record in enumerate(records, 1):
            write_json(destination / "decisions" / f"{number:02d}.json", record.model_dump(mode="json"))
        events = [dict(zip(("revision", "kind", "payload", "recorded_at", "pending"), row)) for row in
            catalog.db.execute("SELECT revision,kind,payload,recorded_at,pending FROM events ORDER BY revision")]
        write_jsonl(destination, "events", events)
    assert file_digest(baseline) == before_hash
    assert after["clasificacion"] == {"certificado": 12, "pendiente": 3, "excluido": 4}
    report = {"status": "passed", "request_digest": request_digest(request), "reused": reused,
        "reviewed_at": records[0].decision.revisado_en.isoformat(),
        "effective_to_exclusive": request.effective_to.isoformat(), "before": before, "after": after,
        "baseline": baseline_summary, "baseline_unchanged_sha256": before_hash,
        "backup_sha256": {p.name: file_digest(p) for p in destination.glob("*.sqlite3")}}
    write_json(destination / "summary.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
