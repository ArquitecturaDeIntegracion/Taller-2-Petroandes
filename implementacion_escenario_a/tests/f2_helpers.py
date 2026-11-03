"""Fixtures ficticios aislados: no son aprobaciones ni respuestas del corpus."""
import hashlib
from datetime import datetime, timedelta, timezone

from petroandes.catalog.api import Catalog
from petroandes.contracts.common import Scope
from petroandes.contracts.documents import Decision, Document
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import DecisionRecord, ServiceContext

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
SCOPE = Scope(tipo="tramo", identificador="TRAMO-SINTETICO")


def doc(code="SINTETICO", content="PDF de prueba"):
    return Document(doc_id=code, version_documental=None,
        pdf_sha256=hashlib.sha256(content.encode()).hexdigest(), tipo="comunicacion",
        titulo="Fixture sintético", emisor="EMISOR-SINTETICO", fecha_emision="2026-01-01",
        pdf_uri=f"project:fixtures/{code}.pdf", paginas=1)


def catalog(tmp_path, perfil="laboratorio"):
    return Catalog.create(tmp_path / perfil / "catalog.sqlite3", perfil)


def record(document, revision, **changes):
    data = dict(doc_id=document.doc_id, version_documental=document.version_documental,
        pdf_sha256=document.pdf_sha256, decision_id=f"FIXTURE-{revision}", perfil="laboratorio",
        simulacion_academica=True, estado="certificado", evidencia=("EVIDENCIA-SINTETICA",),
        autoridad="ROL-FICTICIO", revisor_humano="REVISOR-FICTICIO", revisado_en=NOW - timedelta(days=2),
        effective_from=NOW - timedelta(days=1), effective_to=NOW + timedelta(days=1),
        ambitos=(SCOPE,), usos=("recomendacion",), grupos=("GRUPO-FICTICIO",),
        revision_gobierno=revision)
    return DecisionRecord(decision=Decision(**(data | changes)),
                          supuesto="Ensayo técnico sintético sin validez académica",
                          autenticidad="verificada")


def context(**changes):
    return ServiceContext(**(dict(identidad="USUARIO-FICTICIO", grupos=frozenset(["GRUPO-FICTICIO"]),
                                  ambito=SCOPE, uso="recomendacion") | changes))


def policy(store, ctx=None, at=NOW):
    return EligibilityService(store, ctx or context(), clock=lambda: at)
