"""Controles técnicos F6 con PDF, gobierno, embeddings y Qdrant reales."""
import json
import sqlite3
from contextlib import closing
from datetime import timedelta

import pytest

from historical_lab import historical_lab
from petroandes.compose import answer, service as composition
from petroandes.compose.intent import Intent, resolve
from petroandes.compose.tables import table_units
from petroandes.compose.units import is_anchor, section_units
from petroandes.contracts.documents import Fragment
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.governance.models import Conflict, Identity
from petroandes.retrieve.index import authorized_records


@pytest.fixture(scope="module")
def lab(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        with historical_lab(tmp_path_factory.mktemp("f6"), patch) as data:
            yield data


def report(lab, text, **kwargs):
    service, _ = lab
    return answer(service, SearchQuery(consulta=text, top_k=10, **kwargs))


@pytest.mark.parametrize("text,code,sections,required,forbidden", [
    ("Para el tramo Caucasia-Coveñas, indique el umbral de anomalía de presión y su ventana.",
     "PRO-OPE-012", {"3"}, ("por debajo del umbral", "920", "15 minutos", "psi"), ("Cusiana", "1.250")),
    ("Transcriba el renglón de presión de descarga de la ficha para P-101.",
     "FIC-ACT-P101", {"2"}, ("Valor de diseño", "Límite de alarma", "1.180 psi", "1.240 psi"), ("Caudal",)),
    ("Localice el límite de incertidumbre de medición de RES-CREG-0043-2024.",
     "RES-CREG-0043-2024", {"articulo-2"}, ("0,3 %", "no excederá", "sin versión"), ("0,5 %",)),
    ("Localice el criterio de tolerancia de conciliación de PRO-MED-007 v2.",
     "PRO-MED-007", {"3"}, ("0,5 % del volumen recibido",), ("0,3 %",)),
    ("Muestre los pasos de la secuencia de PRO-OPE-021 v1 junto a sus condiciones.",
     "PRO-OPE-021", {"1", "2", "3", "4"}, ("setenta y dos horas", "Autorización del Centro",
      "1 | Presurización", "5 | Estabilización", "obliga a detener la secuencia"), ()),
    ("Según COM-PRV-0098, cite la recomendación de lubricación y su alcance.",
     "COM-PRV-0098", {"asunto", "antecedente", "recomendacion", "alcance"}, (
         "cuatro meses", "no modifica los planes", "actualización del manual"), ()),
    ("Identifique el firmware anunciado por COM-PRV-0134 y las condiciones de aplicación.",
     "COM-PRV-0134", {"asunto", "contenido-de-la-version", "condiciones-de-aplicacion"}, (
         "7.4", "fuera de servicio", "verificación del factor"), ("Anexo",)),
    ("Extraiga la decisión registrada en ACTA-CTO-2025-07 sobre exigibilidad.",
     "ACTA-CTO-2025-07", {"4"}, ("no son exigibles hasta la emisión y publicación",), ()),
])
def test_literal_units_and_citations(lab, text, code, sections, required, forbidden):
    _, sources = lab
    result = report(lab, text)
    response, rendered = result["resultado"], result["texto"]
    assert response["estado"] == "respondida", (text, result["traza"])
    assert rendered.startswith("Lectura histórica.")
    assert all(term in rendered for term in required)
    assert all(term not in rendered for term in forbidden)
    assert {part["section_id"] for part in response["evidencia"]} == sections
    assert {part["doc_id"] for part in response["evidencia"]} == {code}
    for claim in response["afirmaciones"]:
        cite, = claim["citas"]
        original = [sources[part["chunk_id"]] for part in response["evidencia"]
                    if part["section_id"] == cite["section_id"] and part["pdf_sha256"] == cite["pdf_sha256"]]
        assert any(set(claim["texto"].splitlines()) <= set(part["texto"].splitlines()) for part in original)
    print(json.dumps({"consulta": text, "respuesta": rendered, "traza": result["traza"]}, ensure_ascii=True))


@pytest.mark.parametrize("text,reason", [
    ("Indique el umbral de alarma de presión.", "ambito_ambiguo"),
    ("Localice el límite de incertidumbre de PRO-MED-007 v2.", "evidencia_insuficiente"),
    ("Localice el MAOP para Ayacucho–Coveñas.", "evidencia_insuficiente"),
    ("Muestre el volumen oficial del tramo en octubre de 2026.", "fuera_del_corpus"),
    ("Indique la incertidumbre observada en la medición de hoy.", "fuera_del_corpus"),
    ("Para Caucasia-Coveñas, ¿cuál es la ventana para presión por encima del umbral?", "evidencia_insuficiente"),
    ("Compare el umbral de presión y el MAOP para Caucasia-Coveñas.", "evidencia_insuficiente"),
    ("¿Cuál es la presión de succión en P-101?", "evidencia_insuficiente"),
])
def test_abstains_without_evidence(lab, text, reason):
    response = report(lab, text)["resultado"]
    assert response["estado"] == "abstencion"
    assert response["motivo_abstencion"] == reason
    assert response["afirmaciones"] == response["evidencia"] == []
    print(json.dumps({"consulta": text, "respuesta": response}, ensure_ascii=True))


def test_ambiguous_filter_and_question(lab):
    result = report(lab, "Indique el umbral de presión en Caucasia-Coveñas.",
                    filtros={"tramo": "Cusiana-Porvenir"})
    assert result["resultado"]["motivo_abstencion"] == "ambito_ambiguo"


def test_annex_is_auditable_and_absent_from_composition(lab):
    service, sources = lab
    result = report(lab, "En COM-PRV-0134 localice el anexo de notas de integración.",
                    filtros={"tipo": "comunicacion"})
    assert result["resultado"]["estado"] == "abstencion" and not result["resultado"]["evidencia"]
    flagged = result["traza"]["descartados_seguridad"]
    assert [sources[key]["section_id"] for key in flagged] == ["anexo-notas-de-integracion"]
    direct = service.obtain(FragmentQuery(doc_id="COM-PRV-0134", version_documental=None,
                                          section_id="anexo-notas-de-integracion"))["resultado"]
    assert direct["estado"] == "encontrado" and direct["partes"][0]["contenido_no_confiable"]
    assert direct["partes"][0]["texto"] not in json.dumps(result, ensure_ascii=False)
    print(json.dumps({"anexo_auditable": flagged, "respuesta": result["resultado"],
                      "traza": result["traza"]}))


def test_section_conditions_and_use_are_required(lab):
    service, _ = lab
    retrieved = service.search(SearchQuery(consulta="PRO-OPE-021", top_k=10))
    folder = service.root / "generations" / retrieved["resultado"]["generation_id"]
    path = folder / "catalog.sqlite3"
    records = authorized_records(path, service.policy.eligible())
    request = SearchQuery(consulta="Muestre la secuencia de PRO-OPE-021 v1.")
    intent, _ = resolve(request, service.policy.context, records)
    anchor = next(part for part, record in records.values() if is_anchor(part, record, intent, "evidencia_historica"))
    broken = {key: value for key, value in records.items()
              if value[0].doc_id != anchor.doc_id or value[0].section_id != "4"}
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        assert section_units(anchor, records, intent, db)
        assert not section_units(anchor, broken, intent, db)
    request = SearchQuery(consulta="Cite la recomendación de lubricación de COM-PRV-0098.")
    intent, _ = resolve(request, service.policy.context, records)
    assert any(is_anchor(part, record, intent, "recomendacion") for part, record in records.values())
    assert not any(is_anchor(part, record, intent, "instruccion_operativa") for part, record in records.values())


def test_revalidates_after_composition(lab, monkeypatch):
    service, _ = lab
    original = composition.compose
    expiration = max(row.decision.effective_to for row in service.policy.catalog.snapshot().decisiones)

    def expire(*args):
        result = original(*args)
        assert result["estado"] == "respondida"
        monkeypatch.setattr(service.policy, "clock", lambda: expiration)
        return result

    monkeypatch.setattr(composition, "compose", expire)
    result = report(lab, "Transcriba el renglón de presión de descarga de P-101.")
    assert result["resultado"]["motivo_abstencion"] == "gobierno_cambio"
    assert result["resultado"]["evidencia"] == result["resultado"]["afirmaciones"] == []
    assert not {"unidades", "candidatos", "descartados_seguridad"} & result["traza"].keys()


def test_conflict_stops_composition(lab):
    service, _ = lab
    policy = service.policy
    catalog = policy.catalog
    documents = policy.eligible().documentos[:2]
    conflict = Conflict(conflict_id="ensayo-f6", documentos=tuple(
        Identity(doc_id=doc.doc_id, version_documental=doc.version_documental) for doc in documents),
        ambito=policy.context.ambito, uso=policy.context.uso, fundamento="Ensayo técnico aislado",
        registrado_por="fixture", effective_from=policy.clock(), effective_to=policy.clock() + timedelta(hours=1))
    catalog.db.execute("BEGIN IMMEDIATE")
    try:
        catalog.add_conflict(conflict, catalog.verify_revision())
        result = report(lab, "Transcriba el renglón de presión de descarga de P-101.")
        assert result["resultado"]["motivo_abstencion"] == "conflicto_documental"
        assert not result["resultado"]["evidencia"]
        assert "generacion" not in result["traza"]["tiempos_ms"]
    finally:
        catalog.db.rollback()


def test_design_row_retains_qualifier_across_parts(lab):
    _, sources = lab
    origin = Fragment.model_validate(next(part for part in sources.values()
                                          if part["doc_id"] == "MAN-OPE-001" and part["section_id"] == "3"))
    # Ensayo del extractor de filas sobre F3. El manual permanece fuera de la consulta gobernada.
    definition, table, _ = origin.texto.split("\n\n")
    first = origin.model_copy(update={"texto": definition})
    second = origin.model_copy(update={"chunk_id": "parte-sintetica-2", "parte": 2, "texto": table})
    intent = Intent("maop", {}, None, "ayacucho-covenas")
    first_unit, row_unit = table_units((first, second), intent)
    assert "no deben utilizarse como umbrales de alarma" in first_unit.text
    assert "MAOP (psi)" in row_unit.text and "1.250" in row_unit.text
    assert "Cusiana" not in row_unit.text
    assert first_unit.source.chunk_id != row_unit.source.chunk_id
    assert not table_units((second,), intent)
