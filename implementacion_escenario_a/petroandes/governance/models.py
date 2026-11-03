"""Datos internos de gobierno; nunca parámetros de autoautorización MCP."""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from petroandes.contracts.common import Contract, Scope, Sha256, Text, Use
from petroandes.contracts.documents import Decision, Document


class Identity(Contract):
    doc_id: Text
    version_documental: Text | None


class PdfEvidence(Contract):
    fuente: Identity
    pdf_sha256: Sha256
    section_id: Text
    pagina: int = Field(strict=True, ge=1)
    cita: Text


class Observation(Contract):
    observation_id: Text
    documento: Identity
    pdf_sha256: Sha256
    estado: Literal["pendiente", "excluido"]
    fundamento: Text
    fuentes: tuple[PdfEvidence, ...] = ()

    @model_validator(mode="after")
    def exclusion_needs_evidence(self):
        if self.estado == "excluido" and not self.fuentes:
            raise ValueError("Exclusión sin evidencia documental")
        return self


class Relation(Contract):
    relation_id: Text
    tipo: Literal["reemplaza", "deroga"]
    desde: Identity
    hacia: Identity
    evidencia: PdfEvidence


class DecisionRecord(Contract):
    decision: Decision
    supuesto: Text | None = None
    autenticidad: Literal["sin_verificar", "verificada"] = "sin_verificar"
    contenido_no_confiable: Literal[True] = True

    @model_validator(mode="after")
    def academic_assumption(self):
        if (self.decision.estado == "certificado" and self.decision.perfil == "laboratorio"
                and not self.supuesto):
            raise ValueError("Decisión académica sin supuesto explícito")
        return self


class Conflict(Contract):
    conflict_id: Text
    documentos: tuple[Identity, ...] = Field(min_length=2)
    ambito: Scope
    uso: Use
    fundamento: Text
    registrado_por: Text
    effective_from: AwareDatetime
    effective_to: AwareDatetime | None = None

    @model_validator(mode="after")
    def interval(self):
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("Intervalo de conflicto inválido")
        return self


class ServiceContext(Contract):
    identidad: Text
    grupos: frozenset[Text] = Field(min_length=1)
    ambito: Scope
    uso: Use


@dataclass(frozen=True)
class Snapshot:
    perfil: str
    revision: int
    documentos: tuple[Document, ...]
    registros: tuple[tuple[str, int], ...]
    observaciones: tuple[Observation, ...]
    decisiones: tuple[DecisionRecord, ...]
    conflictos: tuple[Conflict, ...]


@dataclass(frozen=True)
class Eligibility:
    revision: int
    documentos: tuple[Document, ...]
    motivo: str
    evaluado_en: datetime
