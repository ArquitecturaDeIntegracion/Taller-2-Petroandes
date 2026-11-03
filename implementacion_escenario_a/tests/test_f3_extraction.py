"""PDF real frente a Markdown de contraste; no define respuestas académicas."""
import hashlib

import pytest
from petroandes.extract.contrast import compare_markdown
from petroandes.extract.models import ExtractionReview, Line
from petroandes.extract.pdf import extract_pdf
from petroandes.extract.tables import blocks
from petroandes.paths import PROJECT_ROOT

PDFS = sorted((PROJECT_ROOT / "corpus/pdf").rglob("*.pdf"))


@pytest.mark.parametrize("path", PDFS, ids=lambda path: path.stem)
def test_real_pdf_sections_and_ordered_lexical_contrast(path):
    doc, sections, extraction = extract_pdf(path)
    md = PROJECT_ROOT / "corpus/md" / path.relative_to(PROJECT_ROOT / "corpus/pdf").with_suffix(".md")
    result = compare_markdown(sections, md)
    assert result["status"] == "coincide_lexico_ordenado"
    assert doc.pdf_sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(extraction["layout_pages"]) == doc.paginas
    assert all(1 <= line.page <= doc.paginas for section in sections
               for block in section.blocks for line in block.lines)


def test_wrapped_table_cell_stays_in_its_row():
    raw = [f"{'Tramo':<25}{'Diseño':<20}Alarma", "",
           f"{'Tramo muy largo':<25}{'1.180 psi':<20}1.240 psi",
           "segunda línea", "", "Prosa posterior sin columnas"]
    source = [Line(1, index + 1, text) for index, text in enumerate(raw)]
    result = blocks(source)
    assert result[0].table.rows == (("Tramo muy largo segunda línea", "1.180 psi", "1.240 psi"),)
    assert result[1].text == "Prosa posterior sin columnas"


def test_ambiguous_table_alignment_is_quarantined():
    source = [Line(1, 1, f"{'Campo':<25}Valor"), Line(1, 2, ""),
              Line(1, 3, "          fuera            dato")]
    with pytest.raises(ExtractionReview, match="ambigua"):
        blocks(source)


def test_missing_negation_is_a_contrast_failure(tmp_path):
    path = next(path for path in PDFS if path.stem == "ACTA-CTO-2025-07")
    _, sections, _ = extract_pdf(path)
    original = (PROJECT_ROOT / "corpus/md/04_actas/ACTA-CTO-2025-07.md").read_text()
    altered = tmp_path / "alterado.md"
    altered.write_text(original.replace("no son exigibles", "son exigibles"), encoding="utf-8")
    with pytest.raises(ExtractionReview, match="Diferencia"):
        compare_markdown(sections, altered)


def test_missing_uncertainty_sign_is_a_contrast_failure(tmp_path):
    path = next(path for path in PDFS if path.stem == "MAN-OPE-004_v2")
    _, sections, _ = extract_pdf(path)
    original = (PROJECT_ROOT / "corpus/md/01_manuales/MAN-OPE-004_v2.md").read_text()
    altered = tmp_path / "sin-signo.md"
    altered.write_text(original.replace("±", ""), encoding="utf-8")
    with pytest.raises(ExtractionReview, match="Diferencia"):
        compare_markdown(sections, altered)
