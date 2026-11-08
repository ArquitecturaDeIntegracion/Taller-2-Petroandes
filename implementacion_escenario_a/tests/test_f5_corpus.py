"""Reproduce F3 a F5 en temporales con decisiones académicas ya registradas."""
import json

from petroandes.contracts.queries import FragmentQuery, SearchQuery
from historical_lab import historical_lab


def test_certified_corpus_in_historical_review_context(tmp_path, monkeypatch):
    with historical_lab(tmp_path, monkeypatch) as (service, fragments):
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
