"""Suficiencia documental, partes completas y condiciones citables."""
import json
import re
from collections import defaultdict

from petroandes.index.publication import document_identity
from petroandes.retrieve.ranking import normalized, version_key
from petroandes.retrieve.selection import context_parts
from .intent import fold
from .tables import Unit, table_units

# Familia, uso específico y título del ancla. La lectura histórica conserva la familia.
RULES = {
    "alarma_tramo": ("procedimiento", "instruccion_operativa", r"criterios de deteccion"),
    "presion_activo": ("ficha", "especificacion_activo", r"datos de operacion"),
    "maop": ("manual", "limite_diseno", r"parametros de diseno"),
    "incertidumbre": ("resolucion", "referencia_normativa", r"incertidumbre"),
    "tolerancia": ("procedimiento", "instruccion_operativa", r"criterios de aceptacion"),
    "secuencia": ("procedimiento", "instruccion_operativa", r"\bsecuencia\b"),
    "recomendacion": ("comunicacion", "recomendacion", r"^recomendacion$"),
    "firmware": ("comunicacion", "recomendacion", r"^asunto$"),
    "acta": ("acta", "evidencia_historica", r"\bdecisiones\b"),
}
TABLE_KINDS = {"alarma_tramo", "presion_activo", "maop"}


def blocked(fragment, record):
    flags = record["metadata"].get("seguridad", {}).get("security_flags", ())
    return fragment.section_id.startswith("anexo-") or "instrucciones_dirigidas_al_procesador" in flags


def is_anchor(fragment, record, intent, use):
    family, permitted, title = RULES[intent.kind]
    if record["metadata"]["documento"]["tipo"] != family or use not in (permitted, "evidencia_historica"):
        return False
    if intent.documents:
        versions = intent.documents.get(normalized(fragment.doc_id), ())
        if None not in versions and version_key(fragment.version_documental) not in versions:
            return False
    tags = record["metadata"].get("semantica_observada", {}).get("activo_tags_observados", ())
    if intent.asset and intent.asset not in {normalized(tag) for tag in tags}:
        return False
    return bool(re.search(title, fold(fragment.titulo_seccion)))


def complete(parts, records, db):
    grouped = defaultdict(list)
    for part in parts:
        if not part.parent_id or blocked(part, records[part.chunk_id][1]):
            return False
        grouped[part.parent_id].append(part)
    for parent_id, group in grouped.items():
        row = db.execute("SELECT payload FROM parents WHERE parent_id=?", (parent_id,)).fetchone()
        if not row or json.loads(row[0]).get("chunk_ids") != [part.chunk_id for part in group]:
            return False
    return bool(grouped)


def section_units(anchor, records, intent, db):
    kind = intent.kind
    related = context_parts(anchor.chunk_id, records)
    local = [part for part in related if part.parent_id == anchor.parent_id]
    if kind in TABLE_KINDS:
        return table_units(local, intent) if complete(local, records, db) else ()

    # Una condición se cita desde su propio fragmento, no desde el contexto E5.
    links = {item["section_id"] for item in records[anchor.chunk_id][1].get("common_context", ())}
    if not links.issubset(part.section_id for part in related):
        return ()
    additional = {
        "secuencia": {"objeto", "alcance"},
        "recomendacion": {"asunto", "antecedente", "alcance"},
        "firmware": {"contenido de la version", "condiciones de aplicacion"},
    }.get(kind, set())
    sections = {part.chunk_id: part for part in related}
    for part, _ in records.values():
        if document_identity(part) != document_identity(anchor):
            continue
        title = re.sub(r"^\d+[.]\s*", "", fold(part.titulo_seccion))
        if title in additional:
            sections[part.chunk_id] = part
    parts = sorted(sections.values(), key=lambda part: part.orden)
    titles = {re.sub(r"^\d+[.]\s*", "", fold(part.titulo_seccion)) for part in parts}
    if kind == "secuencia" and (not links or "objeto" not in titles):
        return ()
    if kind in ("firmware", "recomendacion") and not additional.issubset(titles):
        return ()
    if not complete(parts, records, db):
        return ()
    text = fold(" ".join(part.texto for part in local))
    required = {
        "incertidumbre": r"incertidumbre.*\d\s*%",
        "tolerancia": r"tolerancia.*\d\s*%",
        "firmware": r"version\s+\d+(?:[.]\d+)+.*firmware",
    }.get(kind)
    if required and not re.search(required, text, re.S):
        return ()
    return tuple(Unit(part, part.texto) for part in parts)
