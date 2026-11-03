"""Comprueba el bundle acordado contra pooling manual y rechaza truncamiento."""
from time import perf_counter
from project_paths import MODELS_DIR, model_reference

from f0_common import ROOT, hashes, memory

MODEL = "intfloat/multilingual-e5-small"
REVISION = "fd1525a9fd15316a2d503bf26ab031a61d056e98"
BUNDLE = "e5small-es-1.0.0"


def encode_checked(model, texts):
    lengths = [len(ids) for ids in model.tokenizer(texts, truncation=False)["input_ids"]]
    if max(lengths, default=0) > 448:
        raise ValueError("Entrada E5 superior a 448 tokens; particionar antes de vectorizar")
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def probe(offline):
    import numpy as np
    import torch
    from huggingface_hub import snapshot_download
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(2)
    start_memory = memory()
    start = perf_counter()
    snapshot = snapshot_download(MODEL, revision=REVISION, local_files_only=offline,
        local_dir=MODELS_DIR / f"e5-{REVISION}",
        allow_patterns=["config.json", "model.safetensors", "tokenizer.json",
                        "tokenizer_config.json", "special_tokens_map.json",
                        "sentencepiece.bpe.model", "modules.json",
                        "sentence_bert_config.json", "1_Pooling/config.json"])
    download_seconds = perf_counter() - start
    start = perf_counter()
    model = SentenceTransformer(snapshot, device="cpu", local_files_only=True,
                                trust_remote_code=False)
    model.max_seq_length = 448
    load_seconds = perf_counter() - start
    texts = ["query: ¿Qué información contiene el manual de mantenimiento?",
             "passage: El manual de mantenimiento describe las inspecciones del equipo."]
    batch = model.tokenizer(texts, padding=True, truncation=False, return_tensors="pt")
    lengths = batch["attention_mask"].sum(dim=1).tolist()
    assert max(lengths) <= 448
    start = perf_counter()
    actual = encode_checked(model, texts)
    first_inference_seconds = perf_counter() - start
    start = perf_counter()
    repeated = encode_checked(model, texts)
    inference_seconds = perf_counter() - start
    assert np.allclose(actual, repeated, atol=1e-6)
    with torch.inference_mode():
        output = model[0].auto_model(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1).to(output.dtype)
        manual = torch.nn.functional.normalize((output * mask).sum(1) / mask.sum(1), dim=1)
    delta = float(np.max(np.abs(actual - manual.numpy())))
    assert actual.shape == (2, 384), actual.shape
    assert np.isfinite(actual).all()
    assert np.allclose(np.linalg.norm(actual, axis=1), 1.0, atol=1e-5)
    assert delta < 1e-5, delta
    overlong = "passage: " + "inspección mantenimiento " * 500
    long_count = len(model.tokenizer(overlong, truncation=False)["input_ids"])
    assert long_count > 448
    try:
        encode_checked(model, [overlong])
    except ValueError:
        pass
    else:
        raise AssertionError("El adaptador aceptó una entrada excedida")
    return {"status": "passed", "model": MODEL, "revision": REVISION,
            "bundle": BUNDLE, "tokenizer_revision": REVISION, "device": "cpu",
            "threads": torch.get_num_threads(), "snapshot_ref": model_reference(snapshot),
            "download_or_cache_resolution_seconds": download_seconds,
            "load_seconds": load_seconds, "warm_inference_seconds": inference_seconds,
            "first_inference_after_load_seconds": first_inference_seconds,
            "texts": texts, "token_lengths": lengths, "shape": list(actual.shape),
            "norms": np.linalg.norm(actual, axis=1).tolist(),
            "cosine_query_passage": float(actual[0] @ actual[1]),
            "manual_masked_mean_l2_max_abs_difference": delta,
            "overlong_token_count": long_count, "overlong_sent_to_model": False,
            "memory_before": start_memory, "memory_after": memory(),
            "sha256": hashes(snapshot), "scope": "Compatibilidad, no evaluación de recuperación"}
