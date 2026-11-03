"""Tipos comunes del contrato corpus_documental_petroandes 1.0.0."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

Text = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]
Sha256 = Annotated[str, StringConstraints(strict=True, pattern=r"^[a-f0-9]{64}$")]
DocumentType = Literal["manual", "procedimiento", "resolucion", "acta",
                       "comunicacion", "ficha"]
Use = Literal["instruccion_operativa", "limite_diseno", "especificacion_activo",
              "referencia_normativa", "evidencia_historica", "recomendacion",
              "inspeccion_no_confiable"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Scope(Contract):
    """Un alcance explícito: no interpretar campos ausentes como acceso universal."""
    tipo: Literal["activo", "tramo", "general"]
    identificador: Text


class DocumentReference(Contract):
    doc_id: Text
    version_documental: Text | None
    pdf_sha256: Sha256
