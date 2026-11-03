"""Controles con datos sintéticos; no son casos académicos del corpus."""
import hashlib
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from petroandes.contracts.documents import Decision, Fragment, Manifest
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.contracts.responses import Citation, Claim, FragmentResponse, SearchResponse

DIGEST = hashlib.sha256(b"fixture sintetico, no documento del corpus").hexdigest()


def fragment(**changes):
    fields = dict(doc_id="SINTETICO", version_documental=None, pdf_sha256=DIGEST,
        chunk_id="SINTETICO-seccion-1", section_id="1", titulo_seccion="Prueba",
        pagina_inicio=1, pagina_fin=1, parte=1, orden=0, parent_id=None,
        texto="La puerta de prueba es azul.", parser_version="fixture-1",
        particion="structural-es-1.0.0", bundle="e5small-es-1.0.0", tokens_entrada=12)
    return Fragment(**(fields | changes))


def citation(**changes):
    return Citation(**(dict(doc_id="SINTETICO", version_documental=None,
        pdf_sha256=DIGEST, section_id="1", pagina_inicio=1, pagina_fin=1) | changes))


@pytest.mark.parametrize("extra", ["perfil", "grupos", "vigencia", "prioridad", "identidad"])
def test_public_queries_reject_self_assigned_authority(extra):
    with pytest.raises(ValidationError):
        SearchQuery.model_validate({"consulta": "Prueba", extra: "administrador"})
    with pytest.raises(ValidationError):
        FragmentQuery.model_validate({"doc_id": "SINTETICO", "version_documental": None,
                                      "section_id": "1", extra: "administrador"})


@pytest.mark.parametrize("query", ["", "   ", "a" * 2001])
def test_invalid_question_lengths(query):
    with pytest.raises(ValidationError):
        SearchQuery(consulta=query)


@pytest.mark.parametrize("top_k", [0, 11, "5", True])
def test_top_k_limits_and_types(top_k):
    with pytest.raises(ValidationError):
        SearchQuery(consulta="Prueba", top_k=top_k)


def test_nullable_version_is_explicit_and_not_coerced():
    assert FragmentQuery(doc_id="SINTETICO", version_documental=None,
                         section_id="1").version_documental is None
    with pytest.raises(ValidationError):
        FragmentQuery(doc_id="SINTETICO", section_id="1")
    with pytest.raises(ValidationError):
        FragmentQuery(doc_id="SINTETICO", version_documental=1, section_id="1")


def test_incomplete_certification_is_rejected():
    data = dict(doc_id="SINTETICO", version_documental=None, pdf_sha256=DIGEST,
                decision_id="fixture", perfil="baseline", simulacion_academica=False,
                estado="pendiente", evidencia=("Prueba sintética",), revision_gobierno=0)
    assert Decision(**data).estado == "pendiente"
    with pytest.raises(ValidationError):
        Decision(**(data | {"estado": "certificado"}))
    with pytest.raises(ValidationError):
        Decision(**(data | {"simulacion_academica": True}))
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        Decision(**(data | {"effective_from": now, "effective_to": now - timedelta(days=1)}))


@pytest.mark.parametrize("changes", [{"tokens_entrada": 449}, {"pagina_inicio": 2},
    {"contenido_no_confiable": False}, {"bundle": "otro-bundle"}, {"pdf_sha256": "falso"}])
def test_fragment_integrity(changes):
    with pytest.raises(ValidationError):
        fragment(**changes)


def test_claim_needs_citation_and_response_matches_provenance():
    with pytest.raises(ValidationError):
        Claim(texto="Texto de prueba", citas=())
    result = dict(estado="respondida", correlation_id=uuid4(), generation_id="fixture",
                  revision_gobierno=0, evidencia=(fragment(),))
    SearchResponse(**result, afirmaciones=(Claim(texto=fragment().texto, citas=(citation(),)),))
    with pytest.raises(ValidationError):
        SearchResponse(**result, afirmaciones=(Claim(texto="Prueba",
                       citas=(citation(doc_id="OTRO-SINTETICO"),)),))


def test_denials_and_abstentions_do_not_expose_fragments():
    result = dict(correlation_id=uuid4(), generation_id=None, revision_gobierno=0)
    SearchResponse(**result, estado="abstencion", motivo_abstencion="sin_evidencia_autorizada")
    with pytest.raises(ValidationError):
        SearchResponse(**result, estado="abstencion", motivo_abstencion="fuera_del_corpus",
                       evidencia=(fragment(),))
    with pytest.raises(ValidationError):
        FragmentResponse(**result, estado="denegado", error="evidencia_no_autorizada",
                         partes=(fragment(),))


def test_manifest_rejects_duplicate_chunk_ids():
    with pytest.raises(ValidationError):
        Manifest(generation_id="fixture", perfil="baseline", revision_gobierno=0,
            particion="structural-es-1.0.0", bundle="e5small-es-1.0.0", dimension=384,
            distancia="cosine", catalogo_sha256=DIGEST, proyeccion_densa_sha256=DIGEST,
            proyeccion_lexica_sha256=DIGEST, fragmentos=("fixture", "fixture"))


def test_unknown_end_is_not_an_approved_open_period():
    now = datetime.now(timezone.utc)
    data = dict(doc_id="SINTETICO", version_documental=None, pdf_sha256=DIGEST,
        decision_id="fixture", perfil="laboratorio", simulacion_academica=True,
        estado="certificado", evidencia=("Prueba sintética",), revision_gobierno=0,
        autoridad="ROL-SINTETICO", revisor_humano="REVISOR-SINTETICO", revisado_en=now,
        effective_from=now, ambitos=({"tipo": "general", "identificador": "fixture"},),
        usos=("evidencia_historica",), grupos=("grupo-sintetico",))
    with pytest.raises(ValidationError):
        Decision(**data)
    assert Decision(**data, intervalo_abierto_expreso=True).effective_to is None
