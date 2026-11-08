"""Prefiltros de consulta, coincidencia de códigos y fusión por posiciones."""
import re
import unicodedata
from fractions import Fraction

from petroandes.index.projections import tokens

RRF_K = 60
MIN_DEPTH = 10
EXACT_VERSION = "codes-es-1.0.0"
ASSET_ALIASES = {"p101": "p-101"}
CODE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+")
VERSION = re.compile(r"v\d+(?:[.]\d+)*")
VERSION_NUMBER = re.compile(r"\d+(?:[.]\d+)*")


def normalized(text):
    return unicodedata.normalize("NFC", text).casefold()


def normalized_segment(text):
    return re.sub(r"\s*[-–—]\s*", "-", normalized(text))


def filter_records(records, filters):
    if filters is None:
        return records
    active = normalized(filters.activo) if filters.activo else None
    active = ASSET_ALIASES.get(active, active)
    segment = normalized_segment(filters.tramo) if filters.tramo else None
    result = {}
    for key, (fragment, record) in records.items():
        metadata = record["metadata"]
        observed = metadata.get("semantica_observada", {})
        if filters.tipo and metadata["documento"]["tipo"] != filters.tipo:
            continue
        if active and active not in {normalized(tag) for tag in observed.get("activo_tags_observados", ())}:
            continue
        if segment and segment not in {normalized_segment(tag) for tag in observed.get("tramos_observados", ())}:
            continue
        result[key] = (fragment, record)
    return result


def query_codes(text):
    words = tokens(normalized(text))
    identities = {}
    standalone = False
    for index, word in enumerate(words):
        code = ASSET_ALIASES.get(word, word)
        if not CODE.fullmatch(code) or not any(char.isdigit() for char in code):
            continue
        suffix = words[index + 1:index + 3]
        version_label = bool(suffix and suffix[0] in ("versión", "version"))
        if version_label:
            suffix = suffix[1:]
        value = suffix[0] if suffix else ""
        version = value.removeprefix("v") if VERSION.fullmatch(value) or (
            version_label and VERSION_NUMBER.fullmatch(value)) else None
        if index == 0:
            standalone = len(words) == 1 or (version is not None and len(words) == 2 + version_label)
        identities.setdefault(code, set()).add(version)
    return identities, standalone


def version_key(version):
    value = normalized(version) if version else None
    return value.removeprefix("v") if value and VERSION.fullmatch(value) else value


def exact_matches(text, records):
    identities, standalone = query_codes(text)
    result = set()
    for key, (fragment, record) in records.items():
        versions = identities.get(normalized(fragment.doc_id), ())
        version = version_key(fragment.version_documental)
        tags = record["metadata"].get("semantica_observada", {}).get("activo_tags_observados", ())
        if None in versions or version in versions or any(
                None in identities.get(normalized(tag), ()) for tag in tags):
            result.add(key)
    return result, standalone


def fuse(dense, lexical, exact_ids, limit):
    scores = {}
    for ranking in (dense, lexical):
        for rank, key in enumerate(dict.fromkeys(ranking), 1):
            scores[key] = scores.get(key, 0) + Fraction(1, RRF_K + rank)
    return sorted(scores, key=lambda key: (-scores[key], key not in exact_ids, key))[:limit]
