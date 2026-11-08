"""Composición F6 dentro de la lectura gobernada de F5."""
import sqlite3
from collections import defaultdict
from contextlib import closing

from petroandes.contracts.responses import Claim, SearchResponse
from petroandes.retrieve.selection import citation
from petroandes.retrieve.service import abstention
from .intent import RULE_VERSION, resolve
from .units import TABLE_KINDS, blocked, is_anchor, section_units


def compose(query, context, ranked, records, folder, trace):
    trace.update({"compositor": RULE_VERSION, "uso": context.uso})
    flagged = [key for key in ranked if blocked(*records[key])]
    if flagged:
        trace["descartados_seguridad"] = flagged
    intent, reason = resolve(query, context, records)
    if reason:
        return abstention(reason)
    trace["criterio"] = intent.kind
    if intent.kind not in TABLE_KINDS and (intent.asset or intent.segment):
        return abstention("evidencia_insuficiente")

    groups = {}
    for key in ranked:
        part, record = records[key]
        if key not in flagged and is_anchor(part, record, intent, context.uso):
            groups.setdefault(part.parent_id, part)
    path = (folder / "catalog.sqlite3").resolve().as_uri()
    with closing(sqlite3.connect(path + "?mode=ro", uri=True)) as db:
        options = [units for part in groups.values() if (units := section_units(part, records, intent, db))]
    if not options:
        return abstention("evidencia_insuficiente")
    if len(options) > 1:
        return abstention("conflicto_documental")

    excerpts = defaultdict(list)
    sources = {}
    claims = []
    for unit in options[0]:
        part = unit.source
        excerpts[part.chunk_id].append(unit.text)
        sources[part.chunk_id] = part
        claims.append(Claim(texto=unit.text, citas=(citation(part),)))
    trace["unidades"] = list(sources)
    evidence = [part.model_copy(update={"texto": "\n\n".join(excerpts[key])}) for key, part in sources.items()]
    return {"estado": "respondida", "afirmaciones": claims, "evidencia": evidence}


USE_LABELS = {
    "evidencia_historica": "Lectura histórica",
    "instruccion_operativa": "Procedimiento documentado",
    "limite_diseno": "Límite de diseño",
    "especificacion_activo": "Especificación del activo",
    "referencia_normativa": "Referencia normativa",
    "recomendacion": "Recomendación documentada",
}


def render(response, use):
    if response.estado == "error":
        return f"Consulta no disponible ({response.error})."
    if response.estado == "abstencion":
        return f"Consulta sin respuesta ({response.motivo_abstencion})."
    paragraphs = [USE_LABELS[use] + ". Extractos documentales."]
    for claim in response.afirmaciones:
        cite = claim.citas[0]
        version = "sin versión" if cite.version_documental is None else f"versión {cite.version_documental}"
        paragraphs.append(f"{claim.texto}\n[{cite.doc_id}, {version}, sección {cite.section_id}, "
                          f"p. {cite.pagina_inicio}–{cite.pagina_fin}]")
    return "\n\n".join(paragraphs)


def answer(retriever, query):
    context = retriever.policy.context
    report = retriever.search(query, compose=lambda ranked, records, folder, trace:
                              compose(query, context, ranked, records, folder, trace))
    response = SearchResponse.model_validate(report["resultado"])
    return report | {"resultado": response.model_dump(mode="json"), "texto": render(response, context.uso)}
