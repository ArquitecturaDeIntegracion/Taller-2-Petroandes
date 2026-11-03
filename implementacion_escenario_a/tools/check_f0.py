"""Cierra F0 solo con evidencia real concordante, sin declarar completada la aplicación."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from project_paths import PROJECT_ROOT, relative_path, resolve_model_report
from lock_compat import lock_matches
from f0_common import ROOT, hashes, write_report


def normalized(hashes):
    return {key.replace("\\", "/"): value for key, value in hashes.items()}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", default="evidence/f0")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    evidence = ROOT / args.evidence_dir
    checks = []

    def verify(name, condition):
        checks.append({"check": name, "passed": bool(condition)})

    inventory = read(evidence / "preflight-final/stdout-001.log")
    verify("inventory_sources_and_19_pairs", not inventory["errors"]
           and inventory["corpus_pdf_count"] == inventory["corpus_md_count"] == 19)
    registry = read(ROOT / "knowledge/sources.json")
    verify("original_registered_sources_unchanged", all(
        hashlib.sha256(relative_path(s["path"], PROJECT_ROOT).read_bytes()).hexdigest() == s["sha256"]
        for s in registry["sources"]))
    corpus = read(evidence / "corpus.json")
    verify("19_readable_pdfs_and_bytes_preserved", corpus["status"] == "passed" and all(
        hashlib.sha256(relative_path(doc["pdf"], PROJECT_ROOT).read_bytes()).hexdigest() == doc["pdf_sha256"]
        for doc in corpus["documents"]) and len(corpus["documents"]) == 19)
    environment = read(evidence / "environment-final.json")
    verify("isolated_environment_and_hardware_recorded", environment["isolated"]
           and environment["cpu"] and environment["memory"]["system_total_bytes"] > 0)
    dependencies = read(evidence / "dependencies.json")
    lock = ROOT / "requirements.lock"
    verify("lock_digest", hashlib.sha256(lock.read_bytes()).hexdigest()
           == dependencies["python_lock_sha256"])
    verify("installed_runtime_versions_match_portable_lock",
           lock_matches(ROOT / "requirements-portable.lock"))
    verified = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True)
    verify("pip_check", verified.returncode == 0)
    storage = read(evidence / "storage-fixed.json")
    verify("qdrant_persistence_prefilter_and_single_owner", storage["status"] == "passed"
           and storage["filtered_ids"] == storage["reopened_ids"] == [1]
           and storage["second_owner_exit_code"] == 23 and not storage["server_used"])
    first_e5 = read(evidence / "e5-materialized.json")
    second_e5 = read(evidence / "e5-offline-timing.json")
    verify("e5_real_model_pooling_and_offline_reload", first_e5["status"] == "passed"
           and second_e5["status"] == "passed" and second_e5["offline_requested"]
           and first_e5["sha256"] == second_e5["sha256"]
           and hashes(resolve_model_report(second_e5, "e5")) == normalized(second_e5["sha256"])
           and second_e5["shape"] == [2, 384]
           and second_e5["manual_masked_mean_l2_max_abs_difference"] < 1e-5
           and not second_e5["overlong_sent_to_model"])
    first_laya = read(evidence / "laya-online.json")
    second_laya = read(evidence / "laya-offline.json")
    verify("laya_real_multilingual_and_offline_reload", first_laya["status"] == "passed"
           and second_laya["status"] == "passed" and second_laya["offline_requested"]
           and first_laya["effective_sha256"] == second_laya["effective_sha256"]
           and second_laya["overlong_pair_rejected_before_inference"]
           and hashes(resolve_model_report(second_laya, "laya"))
           == normalized(second_laya["effective_sha256"]))
    for case in ("noul_positive", "noul_negative", "choice_positive", "choice_negative"):
        first = read(evidence / f"laya-online-{case}.json")
        second = read(evidence / f"laya-offline-{case}.json")
        verify(f"laya_{case}_real_repeat", first["matches_synthetic_expectation"]
               and second["matches_synthetic_expectation"]
               and first["answer"] == second["answer"] and not second["truncation"]["truncated"])
    mcp = read(evidence / "mcp-local/summary.json")
    verify("real_inspector_stdio_list_and_call", mcp["status"] == "passed"
           and mcp["listed_tools"] == ["comprobar_entorno"] and mcp["call_result"]["estado"] == "ok")
    complete = all(check["passed"] for check in checks)
    write_report(ROOT / args.output, {"status": "passed" if complete else "failed",
        "phase_F0_complete": complete, "checks": checks, "academic_approvals_created": 0,
        "application_complete": False, "next_phase": "F1 contratos y revisión académica"})
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
