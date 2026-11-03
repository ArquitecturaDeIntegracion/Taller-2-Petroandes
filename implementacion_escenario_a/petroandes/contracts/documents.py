"""Documento, decisión, fragmento y generación; el índice no certifica vigencia."""
from typing import Literal
from datetime import date

from pydantic import AwareDatetime, Field, model_validator

from .common import Contract, DocumentReference, DocumentType, Scope, Sha256, Text, Use


class Document(DocumentReference):
    contrato: Literal["corpus_documental_petroandes/1.0.0"] = "corpus_documental_petroandes/1.0.0"
    tipo: DocumentType
    titulo: Text
    emisor: Text
    fecha_emision: date
    pdf_uri: Text
    paginas: int = Field(strict=True, ge=1)


class Decision(DocumentReference):
    decision_id: Text
    perfil: Literal["baseline", "laboratorio"]
    simulacion_academica: bool = Field(strict=True)
    estado: Literal["pendiente", "certificado", "excluido"]
    evidencia: tuple[Text, ...] = Field(min_length=1)
    autoridad: Text | None = None
    revisor_humano: Text | None = None
    revisado_en: AwareDatetime | None = None
    effective_from: AwareDatetime | None = None
    effective_to: AwareDatetime | None = None
    intervalo_abierto_expreso: bool = Field(default=False, strict=True)
    ambitos: tuple[Scope, ...] = ()
    usos: tuple[Use, ...] = ()
    grupos: tuple[Text, ...] = ()
    revision_gobierno: int = Field(strict=True, ge=0)

    @model_validator(mode="after")
    def coherent_authorization(self):
        if self.simulacion_academica != (self.perfil == "laboratorio"):
            raise ValueError("Las simulaciones pertenecen exclusivamente a laboratorio")
        if self.effective_to is not None:
            if self.effective_from is None or self.effective_to <= self.effective_from:
                raise ValueError("Período efectivo vacío o sin inicio")
            if self.intervalo_abierto_expreso:
                raise ValueError("Un período finito no se rotula como abierto")
        if self.estado == "certificado":
            fields = (self.autoridad, self.revisor_humano, self.revisado_en,
                      self.effective_from, self.ambitos, self.usos, self.grupos)
            if not all(fields):
                raise ValueError("Certificación incompleta; no concede autorización")
            if self.effective_to is None and not self.intervalo_abierto_expreso:
                raise ValueError("Período abierto requiere decisión expresa")
        return self


class Fragment(DocumentReference):
    chunk_id: Text
    section_id: Text
    titulo_seccion: Text
    pagina_inicio: int = Field(strict=True, ge=1)
    pagina_fin: int = Field(strict=True, ge=1)
    parte: int = Field(strict=True, ge=1)
    orden: int = Field(strict=True, ge=0)
    parent_id: Text | None
    texto: Text
    parser_version: Text
    particion: Literal["structural-es-1.0.0"]
    bundle: Literal["e5small-es-1.0.0"]
    tokens_entrada: int = Field(strict=True, ge=1, le=448)
    contenido_no_confiable: Literal[True] = True

    @model_validator(mode="after")
    def page_order(self):
        if self.pagina_fin < self.pagina_inicio:
            raise ValueError("Intervalo de páginas invertido")
        return self


class Manifest(Contract):
    generation_id: Text
    perfil: Literal["baseline", "laboratorio"]
    revision_gobierno: int = Field(strict=True, ge=0)
    particion: Literal["structural-es-1.0.0"]
    bundle: Literal["e5small-es-1.0.0"]
    dimension: Literal[384]
    distancia: Literal["cosine"]
    catalogo_sha256: Sha256
    proyeccion_densa_sha256: Sha256
    proyeccion_lexica_sha256: Sha256
    fragmentos: tuple[Text, ...]

    @model_validator(mode="after")
    def unique_fragments(self):
        if len(self.fragmentos) != len(set(self.fragmentos)):
            raise ValueError("Fragmentos duplicados en la generación")
        return self
