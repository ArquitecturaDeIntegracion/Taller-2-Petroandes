"""Reglas de intención y ámbito para la composición de extractos."""
import re
import unicodedata
from dataclasses import dataclass

from petroandes.retrieve.ranking import ASSET_ALIASES, normalized, normalized_segment, query_codes

RULE_VERSION = "extractiva-es-1.1.0"
DOC_PREFIX = ("acta-", "com-", "fic-", "man-", "pro-", "res-")
EXTERNAL = re.compile(
    r"\b(envi[ae]r?|ejecut[ae]r?|modific[ae]r?|telemetria|en tiempo real|"
    r"(?:cifra|volumen|resultado) oficial|"
    r"(?:presion|caudal|lectura|incertidumbre) (?:actual|de hoy|medid[ao]|observad[ao]))\b"
)
INFERENCE = re.compile(r"\b(compar\w*|equivalen\w*|versus|diferencia entre|"
                       r"calcul\w*|estim\w*|predic\w*|por que|anexo|notas de integracion)\b")
SEGMENT = re.compile(r"(?<![\w-])[^\W\d_]+-[^\W\d_]+(?![\w-])")


def fold(text):
    return "".join(char for char in unicodedata.normalize("NFD", text.casefold())
                   if unicodedata.category(char) != "Mn")


@dataclass(frozen=True)
class Intent:
    kind: str
    documents: dict
    asset: str | None
    segment: str | None


def resolve(query, context, records):
    text = fold(query.consulta)
    if EXTERNAL.search(text):
        return None, "fuera_del_corpus"
    if INFERENCE.search(text):
        return None, "evidencia_insuficiente"

    codes, _ = query_codes(query.consulta)
    documents = {code: versions for code, versions in codes.items() if code.startswith(DOC_PREFIX)}
    if len(documents) > 1 or any(len(versions) > 1 for versions in documents.values()):
        return None, "evidencia_insuficiente"
    observed = [item["metadata"].get("semantica_observada", {}) for _, item in records.values()]
    tags = {normalized(tag) for metadata in observed for tag in metadata.get("activo_tags_observados", ())}
    assets = {code for code in codes if code in tags or re.fullmatch(r"p-\d+", code)}
    if query.filtros and query.filtros.activo:
        value = normalized(query.filtros.activo)
        assets.add(ASSET_ALIASES.get(value, value))
    if context.ambito.tipo == "activo":
        value = normalized(context.ambito.identificador)
        assets.add(ASSET_ALIASES.get(value, value))

    segments = set()
    if query.filtros and query.filtros.tramo:
        segments.add(fold(normalized_segment(query.filtros.tramo)))
    if context.ambito.tipo == "tramo":
        segments.add(fold(normalized_segment(context.ambito.identificador)))
    segment_text = fold(normalized_segment(query.consulta))
    known = {fold(normalized_segment(tag)) for metadata in observed for tag in metadata.get("tramos_observados", ())}
    segments.update(tag for tag in known if re.search(rf"(?<!\w){re.escape(tag)}(?!\w)", segment_text))
    if re.search(r"\b(?:tramo|maop|presion)\b", text):
        segments.update(SEGMENT.findall(segment_text))
    if len(assets) > 1 or len(segments) > 1 or assets and segments:
        return None, "ambito_ambiguo"
    asset, segment = next(iter(assets), None), next(iter(segments), None)

    pressure = bool(re.search(r"\b(presion|presiones)\b", text))
    threshold = bool(re.search(r"\b(alarma|umbral|ventana|anomalia)\b", text))
    matches = {
        "alarma_tramo": pressure and threshold and not asset,
        "presion_activo": pressure and bool(asset) and "descarga" in text,
        "maop": bool(re.search(r"\bmaop\b", text)),
        "incertidumbre": "incertidumbre" in text,
        "tolerancia": "tolerancia" in text and "concili" in text,
        "secuencia": bool(re.search(r"\b(secuencia|pasos)\b", text)),
        "recomendacion": bool(re.search(r"\b(recomend\w*|lubric\w*)\b", text)),
        "firmware": "firmware" in text,
        "acta": ("acta" in text and bool(re.search(r"\b(decision\w*|aprob\w*|exigib\w*)\b", text))),
    }
    kinds = [kind for kind, matches_query in matches.items() if matches_query]
    if len(kinds) != 1:
        return None, "evidencia_insuficiente"
    kind = kinds[0]
    if kind in ("alarma_tramo", "maop") and (not segment or asset):
        return None, "ambito_ambiguo"
    if kind == "alarma_tramo" and re.search(
            r"\b(por encima|supera\w*|aument\w*|superior al umbral|sobre el umbral)\b", text):
        return None, "evidencia_insuficiente"
    if kind in ("secuencia", "recomendacion", "firmware", "acta") and not documents:
        return None, "evidencia_insuficiente"
    return Intent(kind, documents, asset, segment), None
