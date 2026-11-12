"""Controles de acceso y publicaciones F10 sobre un laboratorio desechable."""
from contextlib import closing
from time import perf_counter

from f0_common import write_report
from petroandes.catalog.api import Catalog
from petroandes.catalog.store import document_key
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.index.common import IndexUnavailable
from petroandes.index.dense import DenseOwner
from petroandes.index.propagation import propagate, rollback
from petroandes.index.registry import Registry

CODE = "FIC-ACT-P101"
QUESTION = SearchQuery(consulta=CODE, top_k=5)


def decision(catalog, doc, label, **changes):
    prior = next(row for row in reversed(catalog.snapshot().decisiones)
                 if document_key(row.decision) == document_key(doc) and row.decision.estado == "certificado")
    revision = catalog.verify_revision()
    data = prior.decision.model_dump() | {"decision_id": f"F10-ENSAYO-{label}",
            "revision_gobierno": revision + 1, "pdf_sha256": doc.pdf_sha256,
            "evidencia": (f"ensayo-sintetico-f10:{label}",), "autoridad": "ROL FICTICIO F10",
            "revisor_humano": "FIXTURE TÉCNICO F10"}
    record = type(prior).model_validate({"decision": data | changes,
            "supuesto": "Escenario técnico desechable, sin validez académica",
            "autenticidad": "verificada"})
    catalog.apply_decision(record, revision)
    return perf_counter()


def fixture_document(catalog, code):
    return next(doc for doc in catalog.snapshot().documentos if doc.doc_id == code)


def query_routes(service, fragment):
    question = SearchQuery(consulta=fragment["doc_id"], top_k=5)
    reference = FragmentQuery.model_validate({key: fragment[key] for key in
        ("doc_id", "version_documental", "section_id", "pdf_sha256")})
    return {"busqueda": service.search(question)["resultado"],
            "directa": service.obtain(reference)["resultado"],
            "expansion": service.expand(fragment["chunk_id"])["resultado"]}


def denied_routes(service, fragment, destination, name):
    routes = query_routes(service, fragment)
    write_report(destination / f"{name}.json", routes, emit=False)
    assert routes["busqueda"]["estado"] == "abstencion"
    assert not routes["busqueda"].get("evidencia")
    for route in ("directa", "expansion"):
        assert routes[route]["estado"] == "denegado" and not routes[route]["partes"]
    return routes


def publish(service, stage, destination, name, **options):
    result = propagate(service.root, service.policy, service.encoder, stage, **options)
    snapshot = result.pop("snapshot", None)
    events = result.pop("eventos")
    write_report(destination / f"{name}.json", result | {"eventos_confirmados": len(events)}, emit=False)
    if events:
        from petroandes.extract.output import write_jsonl
        write_jsonl(destination, f"{name}-eventos", events)
    if snapshot is not None:
        publication = result["publicacion"]
        folder = service.root / "generations" / publication["generation_id"]
        manifest = (folder / "manifest.json").read_text(encoding="utf-8")
        (destination / f"{name}-manifiesto.json").write_text(manifest, encoding="utf-8")
    return result | {"eventos": events}


def live_receipt(service):
    with closing(Registry(service.root / "publications.sqlite3", read_only=True)) as registry:
        return registry.active()


def injection():
    raise RuntimeError("F10: interrupción simulada antes de activar")


def race_revoke(service, stage, destination, fragment, catalog_path, patch):
    before = live_receipt(service)
    encoder = service.encoder
    query = encoder.query
    commit = None

    def revoke_during_query(text, *, expected_fingerprint):
        nonlocal commit
        encoded = query(text, expected_fingerprint=expected_fingerprint)
        with Catalog.open(catalog_path, "laboratorio") as writer:
            commit = decision(writer, fixture_document(writer, CODE), "revocacion", estado="excluido")
        return encoded

    with patch.context() as scoped:
        scoped.setattr(encoder, "query", revoke_during_query)
        raced = service.search(QUESTION)
    assert commit is not None
    seconds = perf_counter() - commit
    write_report(destination / "revocacion-en-consulta.json", raced | {"segundos_desde_commit": seconds}, emit=False)
    assert raced["resultado"]["motivo_abstencion"] == "gobierno_cambio"
    assert "seleccionados" not in raced["traza"] and not raced["resultado"].get("evidencia")
    with closing(DenseOwner(service.root / "qdrant")) as owner:
        points = owner.points(before["collection"])
    assert any(point["id"] == fragment["chunk_id"] for point in points)
    write_report(destination / "vector-revocado.json", {"coleccion": before["collection"],
                 "puntos_presentes": len(points), "chunk_id_revocado": fragment["chunk_id"]}, emit=False)
    denied_routes(service, fragment, destination, "revocado-tres-rutas")
    fail = publish(service, stage, destination, "fallo-activacion", before_activate=injection)
    assert fail["status"] == "failed" and len(fail["intentos"]) == 3
    assert service.policy.catalog.pending_events()[0][0] == 14
    assert live_receipt(service) == before
    denied_routes(service, fragment, destination, "fallo-no-publica")

    calls = 0

    def crash_before_ack():
        nonlocal calls
        calls += 1
        if calls == 1:
            assert service.policy.catalog.pending_events()[0][0] == 14
            raise RuntimeError("F10: interrupción simulada después de activar y antes de confirmar")

    recovered = publish(service, stage, destination, "recuperacion", before_ack=crash_before_ack)
    assert recovered["status"] == "passed" and len(recovered["intentos"]) == 2
    assert recovered["publicacion"]["reused"] and not service.policy.catalog.pending_events()
    assert [row["revision"] for row in recovered["eventos"]] == [14]
    active = live_receipt(service)
    for revision in (14, 1):
        duplicate = publish(service, stage, destination, f"replay-{revision}", event_revision=revision)
        assert duplicate["resultado"] == "evento_ya_confirmado" and live_receipt(service) == active
    generation = before["key"]["generation_id"]
    try:
        rollback(service.root, service.policy, encoder, generation)
    except IndexUnavailable as error:
        write_report(destination / "rollback-rechazado.json", {"generation_id": generation,
                     "motivo": str(error), "activa": active["key"]["generation_id"]}, emit=False)
    else:
        raise AssertionError("La reversión rehabilitó una revisión antigua")
    assert live_receipt(service) == active
    return seconds
