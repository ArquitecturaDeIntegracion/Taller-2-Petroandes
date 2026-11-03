"""Salidas extractivas y abstenciones: la validación estructural no prueba relevancia."""
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from .common import Contract, DocumentReference, Text
from .documents import Fragment

ErrorCode = Literal["evidencia_no_autorizada", "referencia_ambigua", "indice_no_listo",
                    "servicio_no_disponible"]
AbstentionReason = Literal["sin_evidencia_autorizada", "evidencia_insuficiente",
                           "ambito_ambiguo", "conflicto_documental", "fuera_del_corpus",
                           "gobierno_cambio"]


class Citation(DocumentReference):
    section_id: Text
    pagina_inicio: int = Field(strict=True, ge=1)
    pagina_fin: int = Field(strict=True, ge=1)

    @model_validator(mode="after")
    def page_order(self):
        if self.pagina_fin < self.pagina_inicio:
            raise ValueError("Cita con páginas invertidas")
        return self


class Claim(Contract):
    texto: Text
    citas: tuple[Citation, ...] = Field(min_length=1)


def matches(citation, fragment):
    return (citation.doc_id == fragment.doc_id
            and citation.version_documental == fragment.version_documental
            and citation.pdf_sha256 == fragment.pdf_sha256
            and citation.section_id == fragment.section_id
            and fragment.pagina_inicio <= citation.pagina_inicio
            and citation.pagina_fin <= fragment.pagina_fin)


class SearchResponse(Contract):
    estado: Literal["respondida", "abstencion", "error"]
    correlation_id: UUID
    generation_id: Text | None
    revision_gobierno: int | None = Field(strict=True, ge=0)
    afirmaciones: tuple[Claim, ...] = ()
    evidencia: tuple[Fragment, ...] = ()
    motivo_abstencion: AbstentionReason | None = None
    error: ErrorCode | None = None

    @model_validator(mode="after")
    def coherent_result(self):
        if self.estado == "respondida":
            if not self.afirmaciones or not self.evidencia:
                raise ValueError("Una respuesta exige afirmaciones citadas y evidencia")
            if self.generation_id is None or self.revision_gobierno is None:
                raise ValueError("Falta generación o revisión de gobierno")
            if self.motivo_abstencion or self.error:
                raise ValueError("Respuesta exitosa con error o abstención")
            for claim in self.afirmaciones:
                if any(not any(matches(cite, part) for part in self.evidencia)
                       for cite in claim.citas):
                    raise ValueError("Cita sin procedencia en la evidencia devuelta")
        else:
            if self.afirmaciones or self.evidencia:
                raise ValueError("Abstención/error no devuelve evidencia ni afirmaciones")
            if self.estado == "abstencion" and (not self.motivo_abstencion or self.error):
                raise ValueError("Abstención sin motivo o mezclada con error")
            if self.estado == "error" and (not self.error or self.motivo_abstencion):
                raise ValueError("Error sin código o mezclado con abstención")
        return self


class FragmentResponse(Contract):
    estado: Literal["encontrado", "denegado", "error"]
    correlation_id: UUID
    generation_id: Text | None
    revision_gobierno: int | None = Field(strict=True, ge=0)
    partes: tuple[Fragment, ...] = ()
    citas: tuple[Citation, ...] = ()
    error: ErrorCode | None = None

    @model_validator(mode="after")
    def coherent_result(self):
        if self.estado == "encontrado":
            if not self.partes or len(self.partes) != len(self.citas) or self.error:
                raise ValueError("Fragmento exige partes y citas correspondientes")
            if self.generation_id is None or self.revision_gobierno is None:
                raise ValueError("Falta generación o revisión de gobierno")
            ordering = [part.orden for part in self.partes]
            if ordering != sorted(set(ordering)):
                raise ValueError("Partes desordenadas o duplicadas")
            if any(not matches(cite, part) for cite, part in zip(self.citas, self.partes)):
                raise ValueError("Cita incompatible con su fragmento")
        elif self.partes or self.citas or not self.error:
            raise ValueError("Denegación/error no revela evidencia y exige código")
        if self.estado == "denegado" and self.error != "evidencia_no_autorizada":
            raise ValueError("La denegación usa evidencia_no_autorizada")
        return self
