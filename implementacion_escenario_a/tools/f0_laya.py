"""Sonda multilingüe real: positivos/negativos sintéticos de noul y choice."""
import math
from time import perf_counter
from project_paths import MODELS_DIR, model_reference

from f0_common import ROOT, hashes, memory, write_report

MODEL = "convaiinnovations/laya-multilingual"
REVISION = "e4e9ddf21a7b1903b7acffd8814ad4307bf63a67"
CASES = [
    {"id": "noul_positive", "state": "El informe de prueba registra el color azul.",
     "question": {"type": "noul", "instructions":
                  "¿La evidencia afirma que el color registrado es azul?"}, "expected": True},
    {"id": "noul_negative", "state": "El informe de prueba registra el color azul.",
     "question": {"type": "noul", "instructions":
                  "¿La evidencia afirma que el color registrado es rojo?"}, "expected": False},
    {"id": "choice_positive", "state":
     "Pregunta: ¿De qué color es la puerta? Fragmento: La puerta es azul.",
     "question": {"type": "choice", "instructions":
                  "¿El fragmento responde a la pregunta indicada?", "criteria":
                  {"pertinente": "Sí responde", "no_pertinente": "No responde"}},
     "expected": "pertinente"},
    {"id": "choice_negative", "state":
     "Pregunta: ¿De qué color es la puerta? Fragmento: La factura vence el martes.",
     "question": {"type": "choice", "instructions":
                  "¿El fragmento responde a la pregunta indicada?", "criteria":
                  {"pertinente": "Sí responde", "no_pertinente": "No responde"}},
     "expected": "no_pertinente"},
]


def check_pair(agent, state, question):
    from laya.common import build_sequence

    internal = {"t": question["type"], "ins": question["instructions"],
                "crit": question.get("criteria")}
    seq, _, stats = build_sequence(agent.tok, state, internal, max_len=1024,
        head_max_len=256, return_truncation_stats=True)
    if stats["truncated"]:
        raise ValueError("El par pregunta/evidencia de laya excede 1024 tokens")
    return len(seq), stats


def probe(offline, output):
    import laya
    import torch
    from huggingface_hub import snapshot_download

    torch.set_num_threads(2)
    start_memory = memory()
    start = perf_counter()
    snapshot = snapshot_download(MODEL, revision=REVISION, local_files_only=offline,
        local_dir=MODELS_DIR / f"laya-{REVISION}",
        allow_patterns=["rl_agent_config.json", "model.safetensors", "encoder/*.json",
                        "tokenizer/*"])
    download_seconds = perf_counter() - start
    original_hashes = hashes(snapshot)
    start = perf_counter()
    agent = laya.load(snapshot, device="cpu", backend="eager")
    load_seconds = perf_counter() - start
    observations = []
    for case in CASES:
        question = case["question"]
        sequence_tokens, stats = check_pair(agent, case["state"], question)
        start = perf_counter()
        result = agent.predict(case["state"], {"test": question}, max_len=1024,
                               head_max_len=256)
        elapsed = perf_counter() - start
        answer = result["answers"]["test"]
        if question["type"] == "noul":
            value = answer["noul"]
            assert math.isfinite(value) and 0 <= value <= 1
            matched = (value >= 0.5) == case["expected"]
        else:
            assert set(answer["probabilities"]) == {"pertinente", "no_pertinente"}
            matched = answer["choice"] == case["expected"]
        case_path = output.with_name(f"{output.stem}-{case['id']}.json")
        write_report(case_path, {"synthetic_case": case, "sequence_tokens": sequence_tokens,
            "truncation": stats, "inference_seconds": elapsed, "answer": answer,
            "matches_synthetic_expectation": matched})
        observations.append({"id": case["id"], "evidence": case_path.name,
                             "inference_seconds": elapsed,
                             "matches_synthetic_expectation": matched})
    try:
        check_pair(agent, "evidencia sintética " * 1200, CASES[0]["question"])
    except ValueError:
        pass
    else:
        raise AssertionError("Laya aceptó un par excedido")
    return {"status": "passed", "snapshot_ref": model_reference(snapshot), "model": MODEL, "revision": REVISION,
            "device": str(agent.device), "backend": agent.backend, "threads": 2,
            "download_or_cache_resolution_seconds": download_seconds,
            "load_seconds": load_seconds, "observations": observations,
            "synthetic_disagreements": [r["id"] for r in observations
                                         if not r["matches_synthetic_expectation"]],
            "diagnostic_noul_threshold": 0.5, "calibrated_threshold": None,
            "overlong_pair_rejected_before_inference": True,
            "memory_before": start_memory, "memory_after": memory(),
            "before_load_sha256": original_hashes, "effective_sha256": hashes(snapshot),
            "scope": "Compatibilidad sintética; no son los 15 casos ni calibración académica"}
