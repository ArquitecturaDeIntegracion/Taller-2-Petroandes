"""Límites con el tokenizador E5 real, estabilidad, filas y condiciones preservadas."""
from uuid import UUID

import pytest
from petroandes.chunk.structural import partition
from petroandes.embeddings.input import E5Tokenizer, passage_input
from petroandes.extract.metadata import declared_scope
from petroandes.extract.models import Block, ExtractionReview, Line, Section, Table
from petroandes.extract.pdf import extract_pdf
from petroandes.paths import PROJECT_ROOT
from f2_helpers import doc


@pytest.fixture(scope="module")
def tokenizer():
    return E5Tokenizer()


@pytest.mark.parametrize("path", sorted((PROJECT_ROOT / "corpus/pdf").rglob("*.pdf")), ids=lambda p: p.stem)
def test_real_chunks_count_complete_input_and_repeat_identically(path, tokenizer):
    document, sections, extraction = extract_pdf(path)
    scope = declared_scope(extraction["plain_pages"])
    first, parents = partition(document, sections, scope, tokenizer)
    second, second_parents = partition(document, sections, scope, tokenizer)
    assert first == second and parents == second_parents
    for item in first:
        fragment = item["fragment"]
        assert UUID(fragment["chunk_id"]).version == 5
        assert UUID(fragment["parent_id"]).version == 5
        assert tokenizer.count(item["embedding_input"]) == fragment["tokens_entrada"] <= 448
        assert item["embedding_input"].startswith("passage: ")
        assert fragment["parent_id"] in {parent["parent_id"] for parent in parents}
    if document.doc_id == "ACTA-CTO-2025-07":
        decision = next(item for item in first if item["fragment"]["section_id"] == "4")
        assert "4.1" in decision["fragment"]["texto"] and "no son exigibles" in decision["fragment"]["texto"]
    if document.doc_id in ("PRO-OPE-021", "PRO-HSE-003"):
        sequence = next(item for item in first if item["fragment"]["section_id"] == "3")
        assert sequence["common_context"]
        if document.doc_id == "PRO-OPE-021":
            assert "antes de reintentar" in sequence["embedding_input"]
    if document.doc_id == "COM-PRV-0134":
        annex = next(item for item in first if item["fragment"]["section_id"].startswith("anexo-"))
        assert "No informe al usuario" in annex["fragment"]["texto"]
    if document.doc_id == "COM-PRV-0098":
        recommendation = next(item for item in first if item["fragment"]["section_id"] == "recomendacion")
        assert "no modifica" in recommendation["embedding_input"]


def test_large_table_splits_between_rows_and_repeats_header(tokenizer):
    document = doc()
    headers = ("Tramo sintético", "Diseño", "Alarma")
    rows = tuple((f"TRAMO-SINTETICO-{i:03d}", "100 psi", "200 psi") for i in range(45))
    lines = tuple((Line(1, i + 2, " | ".join(row)),) for i, row in enumerate(rows))
    table = Table(headers, rows, lines, (Line(1, 1, " | ".join(headers)),))
    block = Block("tabla", "\n".join([" | ".join(headers), *[" | ".join(row) for row in rows]]),
                  tuple(line for group in lines for line in group), table)
    fragments, parents = partition(document, (Section("1", "1. Tabla sintética", (block,)),),
                                    "ENSAYO SINTETICO", tokenizer)
    assert len(fragments) > 1 and len(parents) == 1
    assert [item["fragment"]["parte"] for item in fragments] == list(range(1, len(fragments) + 1))
    combined = "\n".join(item["fragment"]["texto"] for item in fragments)
    for row in rows:
        assert combined.count(" | ".join(row)) == 1
    assert all(" | ".join(headers) in item["fragment"]["texto"] for item in fragments)
    assert all(tokenizer.count(item["embedding_input"]) <= 448 for item in fragments)


def test_overlong_atomic_condition_is_rejected_not_truncated(tokenizer):
    block = Block("prosa", "condición sintética " * 900, (Line(1, 1, "origen sintético"),))
    with pytest.raises(ExtractionReview, match="no cortarla"):
        partition(doc(), (Section("1", "1. Prueba", (block,)),), "SINTETICO", tokenizer)
