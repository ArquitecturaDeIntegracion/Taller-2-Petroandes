"""Búsqueda F5, sin composición ni privilegios suministrados en la consulta."""
import sqlite3
from contextlib import ExitStack
from time import perf_counter
from uuid import uuid4

from petroandes.catalog.store import CatalogUnavailable
from petroandes.contracts.responses import FragmentResponse
from petroandes.embeddings.encoder import InputTooLong
from petroandes.index.common import IndexUnavailable
from petroandes.index.projections import LEXICAL_VERSION, lexical_search
from petroandes.index.publication import document_identity
from .index import StaleGeneration, authorized_records, open_generation
from .ranking import EXACT_VERSION, MIN_DEPTH, RRF_K, exact_matches, filter_records, fuse
from .selection import citation, context_parts, direct_parts


def eligibility_key(eligibility):
    return (eligibility.revision, eligibility.motivo,
            frozenset(document_identity(doc) for doc in eligibility.documentos))


def abstention(reason):
    return {"estado": "abstencion", "motivo_abstencion": reason}


def error(code):
    return {"estado": "error", "error": code}


def denied():
    return {"estado": "denegado", "error": "evidencia_no_autorizada"}


class Retriever:
    def __init__(self, root, policy, encoder):
        self.root, self.policy, self.encoder = root.resolve(), policy, encoder

    def search(self, query, *, compose=None):
        def retrieve(view, records, trace, measure):
            owner, manifest, collection, folder = view
            authorized = records
            records = filter_records(records, query.filtros)
            if not records:
                trace["prefiltro_fragmentos"] = 0
                return abstention("sin_evidencia_autorizada")
            depth = max(MIN_DEPTH, query.top_k)
            trace.update({"top_k": query.top_k, "profundidad_rama": depth, "rrf_k": RRF_K,
                          "fusion": "rrf", "tokenizacion": LEXICAL_VERSION, "codigos": EXACT_VERSION,
                          "desempate": "coincidencia_exacta_y_chunk_id"})
            exact, standalone = measure("exacta", lambda: exact_matches(query.consulta, records))
            trace["modo"] = "codigo_exacto" if standalone else "texto"
            if standalone:
                records = {key: value for key, value in records.items() if key in exact}
            trace["prefiltro_fragmentos"] = len(records)
            if not records:
                return abstention("evidencia_insuficiente")
            fingerprint = self.encoder.fingerprint
            vector = measure("embedding", lambda: self.encoder.query(
                query.consulta, expected_fingerprint=fingerprint))
            points = measure("densa", lambda: owner.search(
                collection, vector, records.keys(), generation=manifest.generation_id,
                revision=manifest.revision_gobierno, fingerprint=fingerprint, limit=len(records)))
            dense = [str(point.id) for point in sorted(points, key=lambda point: (-point.score, str(point.id)))[:depth]]
            if not set(dense).issubset(records):
                raise IndexUnavailable("La rama densa devolvió un ID fuera del prefiltro")
            lexical = measure("lexica", lambda: lexical_search(
                folder / "lexical.sqlite3", query.consulta, records.keys(), depth, exact_ids=exact))
            lexical = [key for key, _ in lexical]
            selected = measure("fusion", lambda: fuse(dense, lexical, exact, query.top_k))
            trace["candidatos"] = {"densa": dense, "lexica": lexical, "exacta": sorted(exact)}
            trace["seleccionados"] = selected
            if not selected:
                return abstention("evidencia_insuficiente")
            if compose is not None:
                return measure("composicion", lambda: compose(selected, authorized, folder, trace))
            return {"estado": "recuperada", "evidencia": [records[key][0].model_dump(mode="json") for key in selected],
                    "citas": [citation(records[key][0]) for key in selected]}

        return self._run("responder" if compose is not None else "buscar", retrieve, search=True)

    def obtain(self, query):
        return self._parts("obtener", lambda records: direct_parts(query, records))

    def expand(self, chunk_id):
        return self._parts("expandir", lambda records: context_parts(chunk_id, records))

    def _parts(self, operation, select):
        def retrieve(_view, records, trace, measure):
            parts = measure("seleccion", lambda: select(records))
            if parts is None:
                return error("referencia_ambigua")
            if not parts:
                return denied()
            trace["seleccionados"] = [part.chunk_id for part in parts]
            return {"estado": "encontrado", "partes": parts, "citas": [citation(part) for part in parts]}

        return self._run(operation, retrieve)

    def _run(self, operation, retrieve, *, search=False):
        started = perf_counter()
        identity = {"correlation_id": str(uuid4()), "generation_id": None, "revision_gobierno": None}
        trace = {"operacion": operation, "tiempos_ms": {}}

        def measure(stage, action):
            start = perf_counter()
            try:
                return action()
            finally:
                trace["tiempos_ms"][stage] = (perf_counter() - start) * 1000

        def changed():
            for key in ("candidatos", "seleccionados", "unidades", "descartados_seguridad"):
                trace.pop(key, None)
            return abstention("gobierno_cambio") if search else denied()

        def revalidate(eligibility, result):
            current = measure("revalidacion", self.policy.eligible)
            if eligibility_key(current) != eligibility_key(eligibility):
                return changed()
            return result

        try:
            eligibility = measure("gobierno", self.policy.eligible)
            identity["revision_gobierno"] = eligibility.revision
            if not eligibility.documentos:
                result = revalidate(eligibility, abstention(eligibility.motivo) if search else denied())
            else:
                with ExitStack() as stack:
                    view = measure("generacion", lambda: stack.enter_context(
                        open_generation(self.root, self.policy, eligibility, self.encoder)))
                    identity["generation_id"] = view[1].generation_id
                    records = measure("catalogo_publicado", lambda: authorized_records(
                        view[3] / "catalog.sqlite3", eligibility))
                    result = retrieve(view, records, trace, measure)
                result = revalidate(eligibility, result)
        except StaleGeneration:
            result = changed()
        except InputTooLong:
            trace["entrada_e5_excedida"] = True
            result = abstention("evidencia_insuficiente")
        except CatalogUnavailable:
            result = error("servicio_no_disponible")
        except (OSError, sqlite3.Error, RuntimeError, ValueError, KeyError):
            result = error("indice_no_listo")
        if result["estado"] in ("error", "denegado", "abstencion"):
            trace.pop("candidatos", None)
            trace.pop("seleccionados", None)
            trace.pop("unidades", None)
        if result["estado"] == "error":
            trace.pop("descartados_seguridad", None)
        trace["tiempos_ms"]["total"] = (perf_counter() - started) * 1000
        result = identity | result
        if not search:
            result = FragmentResponse.model_validate(result).model_dump(mode="json")
        return {"resultado": result, "traza": identity | trace}
