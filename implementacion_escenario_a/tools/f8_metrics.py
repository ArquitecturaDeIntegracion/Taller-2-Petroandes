"""Controles de procedencia y denominadores para la prueba técnica de F8."""
from petroandes.contracts.responses import matches


def section(reference):
    return reference.doc_id, reference.version_documental, reference.section_id


def literal_lines(excerpt, original):
    # El compositor puede unir una cabecera con una fila no contigua.
    source_lines = set(original.splitlines())
    return all(line in source_lines for line in excerpt.splitlines() if line.strip())


def assess_case(case, response, trace, sources, judge):
    evidence = getattr(response, "evidencia", ())
    claims = getattr(response, "afirmaciones", ())
    expected = {tuple(reference) for reference in case["secciones"]}
    cited = {section(cite) for claim in claims for cite in claim.citas}
    claim_text = "\n".join(claim.texto for claim in claims)
    observations = []
    for claim in claims:
        original = {part.chunk_id: sources[part.chunk_id] for part in evidence
                    if part.chunk_id in sources and any(matches(cite, part) for cite in claim.citas)}
        citations_ok = all(any(matches(cite, part) for part in original.values()) for cite in claim.citas)
        literal = any(literal_lines(claim.texto, part.texto) for part in original.values())
        if citations_ok:
            judgement = judge.support(claim.texto, "\n\n".join(part.texto for part in original.values()))
        else:
            judgement = {"estado": "no_evaluable", "motivo": "cita_sin_fuente_elegible"}
        observations.append({"citas_validas": citations_ok, "literal_en_fuente": literal, "laya": judgement})

    selected = trace.get("seleccionados", [])[:5] if case["herramienta"] == "buscar_documentos" else []
    retrieved = {section(sources[key]) for key in selected if key in sources}
    ranking_authorized = all(key in sources for branch in trace.get("candidatos", {}).values() for key in branch)
    relevance = [{"chunk_id": key, "seccion": section(sources[key]),
                  "laya": judge.relevance(case["entrada"]["consulta"], sources[key].texto)}
                 for key in selected if key in sources]
    values = response.model_dump(mode="json")
    outcome = all(values.get(key) == expected_value for key, expected_value in case["esperado"].items())
    deviation = (bool(cited - expected) or not ranking_authorized
                 or any(not part["citas_validas"] or not part["literal_en_fuente"]
                        or part["laya"].get("positivo") is False for part in observations))
    return {"resultado_esperado": outcome, "secciones_citadas_esperadas": cited == expected,
            "literales_esperados": all(term in claim_text for term in case["literales"]),
            "candidatos_elegibles": ranking_authorized,
            "recall_at_5": ratio(len(retrieved & expected), len(expected))
            if response.estado == "respondida" and expected else None,
            "anclaje": observations, "pertinencia": relevance, "desviacion_detectada": deviation}


def ratio(numerator, denominator):
    return {"numerador": numerator, "denominador": denominator,
            "valor": numerator / denominator if denominator else None}


def summarize(cases):
    anchors = [item for case in cases for item in case["anclaje"]]
    relevant = [item for case in cases for item in case["pertinencia"]]
    recalls = [case["recall_at_5"]["valor"] for case in cases if case["recall_at_5"] is not None]
    abstentions = [case for case in cases if case["esperaba_abstencion"]]
    return {"procedencia": ratio(sum(item["citas_validas"] and item["literal_en_fuente"] for item in anchors), len(anchors)),
            "anclaje_laya": judge_ratio(anchors), "pertinencia_laya": judge_ratio(relevant),
            "recall_at_5_medio": ratio(sum(recalls), len(recalls)),
            "desviacion_detectada": ratio(sum(case["desviacion_detectada"] for case in cases), len(cases)),
            "abstenciones_correctas": ratio(sum(case["resultado_esperado"] for case in abstentions), len(abstentions)),
            "abstenciones_indebidas": sum(case["estado_observado"] == "abstencion" and not case["esperaba_abstencion"]
                                          for case in cases)}


def judge_ratio(items):
    evaluated = [item["laya"] for item in items if item["laya"]["estado"] == "evaluado"]
    return {**ratio(sum(item["positivo"] for item in evaluated), len(evaluated)),
            "no_evaluables": sum(item["laya"]["estado"] == "no_evaluable" for item in items),
            "errores": sum(item["laya"]["estado"] == "error" for item in items)}
