"""Contratos de ensayo: el plan y los permisos nunca provienen del documento."""
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Contrato(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True)


class Estado(str, Enum):
    PREPARADO = 'preparado'
    EXPUESTO = 'expuesto'
    PROPUESTO = 'propuesto'
    DECIDIDO = 'decidido'
    EVALUADO = 'evaluado'
    INCONCLUSO = 'inconcluso'


class Plan(Contrato):
    identidad: str
    uso: Literal['lectura_educativa'] = 'lectura_educativa'
    documentos: tuple[str, ...]
    herramientas: tuple[str, ...] = ('buscar_documentos', 'obtener_fragmento')
    max_pasos: int = Field(default=2, ge=1, le=10)


class Accion(Contrato):
    herramienta: str
    argumentos: dict[str, Any]


class Borrador(Contrato):
    texto: str
    doc_id: str
    sha256: str


class Caso(Contrato):
    id: str
    amenaza: str
    objetivo: Literal['acciones', 'filtracion', 'contaminacion', 'integridad', 'benigno']
    fragmentos: tuple[str, ...]
    propuestas: tuple[dict[str, Any], ...] = ()
    borrador: dict[str, Any] | None = None
    identidad: str = 'alicia'
    corromper_recurso: bool = False
    decisiones: tuple[str, ...] = ('denegar',)
    motivos: tuple[str, ...]
    lecturas: tuple[str, ...] = ()
    texto_esperado: str | None = None
    capa: str = 'dispatcher_consumidor'


def plan_inicial(identidad='alicia'):
    documento = 'LAB-BR' if identidad == 'bruno' else 'LAB-FW'
    return Plan(identidad=identidad, documentos=(documento,))
