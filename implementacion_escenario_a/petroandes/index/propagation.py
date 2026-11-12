"""Converge al gobierno vigente y confirma el outbox después de publicar."""
import sqlite3
from time import perf_counter

from petroandes.catalog.store import document_key
from petroandes.retrieve.index import authorized_records
from .common import IndexUnavailable, context_data
from .generation import verify
from .publication import Publisher, governance_fence
from .projections import LEXICAL_VERSION
from .reuse import ReusingEncoder, active_receipt, compare_generations, verified_vectors

MAX_ATTEMPTS = 3


def acknowledge(store, revision):
    rows = store.db.execute("SELECT revision,event_id,kind,recorded_at FROM events "
                            "WHERE pending=1 AND revision<=? ORDER BY revision", (revision,)).fetchall()
    store.db.execute("UPDATE events SET pending=0 WHERE pending=1 AND revision<=?", (revision,))
    fields = ("revision", "event_id", "tipo", "registrado_en")
    return [dict(zip(fields, row, strict=True)) for row in rows]


def confirmed_event(store, revision):
    if revision is None:
        return None
    current = store.verify_revision()
    event = store.db.execute("SELECT pending FROM events WHERE revision=?", (revision,)).fetchone()
    if event is None:
        raise ValueError("Revisión de evento desconocida")
    if event == (0,):
        return {"status": "passed", "resultado": "evento_ya_confirmado", "revision_evento": revision,
                "revision_gobierno": current, "intentos": [], "eventos": []}
    return None


def publish_current(root, policy, encoder, stage, *, reindex, before_activate, before_ack):
    store = policy.catalog
    events, comparison = [], {}
    snapshot = None

    def confirm(revision):
        nonlocal snapshot
        snapshot = store.snapshot()
        if before_ack:
            before_ack()
        events.extend(acknowledge(store, revision))

    with Publisher(root, policy, encoder) as publisher:
        reference = active_receipt(publisher)
        previous = {}
        label = reindex
        if reindex is not None and reference is None:
            raise IndexUnavailable("Consolida una generación antes de reindexar")
        if reindex is None and reference is not None:
            key = reference["key"]
            if key["bundle_fingerprint"] == encoder.fingerprint:
                _, inputs, vectors = verified_vectors(publisher, reference)
                previous = {text: vectors[chunk] for chunk, text in inputs.items()}
            if key["stage"] == stage.manifest["generation_id"]:
                label = key.get("reindex")
        encode = ReusingEncoder(encoder, previous)

        def compare(candidate):
            comparison.update(compare_generations(publisher, reference, candidate))

        publication = publisher.publish(stage, before_activate=before_activate, encode=encode, reindex=label,
                                        check_activation=compare if reindex is not None else None,
                                        after_activate=confirm)
        receipt = publisher.registry.registered(publication["generation_id"])
    return {"publicacion": publication, "recibo": receipt, "comparacion": comparison or None,
            "vectores_reutilizados": encode.reused, "vectores_calculados": encode.computed,
            "eventos": events, "snapshot": snapshot}


def propagate(root, policy, encoder, stage, *, attempts=MAX_ATTEMPTS, event_revision=None, reindex=None,
              before_activate=None, before_ack=None):
    if type(attempts) is not int or not 1 <= attempts <= MAX_ATTEMPTS:
        raise ValueError("El máximo de intentos debe estar entre 1 y 3")
    replay = confirmed_event(policy.catalog, event_revision)
    if replay is not None:
        return replay
    history = []
    for attempt in range(1, attempts + 1):
        started = perf_counter()
        try:
            result = publish_current(root, policy, encoder, stage, reindex=reindex,
                                     before_activate=before_activate, before_ack=before_ack)
        except (OSError, sqlite3.Error, RuntimeError, ValueError) as error:
            history.append({"intento": attempt, "estado": "fallido", "tipo": type(error).__name__,
                            "motivo": str(error), "segundos": perf_counter() - started})
        else:
            history.append({"intento": attempt, "estado": "confirmado", "segundos": perf_counter() - started})
            return {"status": "passed", "resultado": "publicacion_verificada", "intentos": history, **result}
    return {"status": "failed", "resultado": "reintentos_agotados", "intentos": history, "eventos": []}


def rollback(root, policy, encoder, generation):
    with Publisher(root, policy, encoder) as publisher:
        receipt = publisher.registry.registered(generation)
        key = receipt["key"]
        if (key["perfil"] != policy.catalog.perfil or key["context"] != context_data(policy.context)
                or key["lexical_version"] != LEXICAL_VERSION):
            raise IndexUnavailable("La generación de reversión pertenece a otro perfil, contexto o motor")
        folder = publisher.root / "generations" / generation
        with governance_fence(policy, key["revision_gobierno"]) as current:
            manifest = verify(folder, receipt, publisher.owner, encoder.fingerprint)
            records = authorized_records(folder / "catalog.sqlite3", current)
            after = policy.eligible()
            if (set(records) != set(manifest.fragmentos)
                    or {document_key(doc) for doc in current.documentos} !=
                    {document_key(doc) for doc in after.documentos}):
                raise IndexUnavailable("La reversión contiene evidencia que ya no es elegible")
            publisher.registry.activate(generation, receipt)
        return {"status": "passed", "generation_id": generation, "revision_gobierno": key["revision_gobierno"],
                "fragmentos": len(manifest.fragmentos)}
