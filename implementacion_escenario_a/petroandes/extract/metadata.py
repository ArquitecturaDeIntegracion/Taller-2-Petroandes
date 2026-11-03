"""Metadatos observados y proyección del gobierno; lo declarado no concede acceso."""
import re

from petroandes.catalog.store import document_key
from petroandes.governance.models import Relation
from .models import ExtractionReview


def declared_scope(plain_pages):
    match = re.search(r"Activo / alcance\s+(.*?)(?=\s+Reemplaza a\s+|\s+1\.\s+|"
                      r"\s+Asunto\b|\s+Considerando\b|\s+Artículo 1\.)", plain_pages[0], re.S)
    if not match:
        raise ExtractionReview("Ámbito declarado PDF no identificable; no asumir alcance")
    return " ".join(match[1].split())


def government_projection(snapshot, document):
    key = document_key(document)
    observations = [item for item in snapshot.observaciones
        if document_key(item.documento) == key and item.pdf_sha256 == document.pdf_sha256]
    excluded = any(item.estado == "excluido" for item in observations)
    latest = next((item.decision for item in reversed(snapshot.decisiones)
                   if document_key(item.decision) == key), None)
    if latest and (latest.pdf_sha256 != document.pdf_sha256
                   or latest.revision_gobierno < dict(snapshot.registros)[key]):
        latest = None
    state = "excluido" if excluded else latest.estado if latest else "pendiente"
    certified = latest if state == "certificado" else None
    return {"governance_revision": snapshot.revision, "perfil": snapshot.perfil, "estado": state,
        "autoridad_certificadora": certified.autoridad if certified else None,
        "decision_id": certified.decision_id if certified else None,
        "certificado_en": certified.revisado_en.isoformat() if certified else None,
        "effective_from": certified.effective_from.isoformat() if certified else None,
        "effective_to": certified.effective_to.isoformat() if certified and certified.effective_to else None,
        "evidencia_decision": list(certified.evidencia) if certified else None,
        "ambitos_autorizados": [scope.model_dump() for scope in certified.ambitos] if certified else None,
        "uso_autorizado": list(certified.usos) if certified else None,
        "grupos_permitidos": list(certified.grupos) if certified else None,
        "clasificacion": None, "restricciones_de_uso": None,
        "motivo": "Exclusión documental" if excluded else "Decisión registrada" if latest else
                  "Falta certificación; null no significa vigente ni público",
        "observaciones": [item.model_dump(mode="json") for item in observations],
        "aplicacion": "proyeccion_informativa; revalidar con la politica antes de consultar"}


def relations_for(catalog, document):
    result = []
    for row in catalog.db.execute("SELECT payload FROM relations ORDER BY relation_id"):
        relation = Relation.model_validate_json(row[0])
        if document_key(document) in (document_key(relation.desde), document_key(relation.hacia)):
            result.append(relation.model_dump(mode="json"))
    return result


def observed_semantics(scope, sections):
    tags = sorted(set(re.findall(r"\b[A-Z]{1,8}(?:-[A-Z0-9]+)+\b", scope)))
    tramos = sorted({row[0] for section in sections for block in section.blocks if block.table
                     and block.table.headers[0] == "Tramo" for row in block.table.rows})
    return {"dominio": "documentacion_del_sistema_de_transporte", "alcance_declarado": scope,
            "activo_tags_observados": tags, "tramos_observados": tramos,
            "fuente": "PDF; atributos observados, no ambitos autorizados"}
