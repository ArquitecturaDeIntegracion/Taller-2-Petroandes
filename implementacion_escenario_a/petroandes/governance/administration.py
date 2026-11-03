"""Entrada administrativa explícita, solo simulaciones; nunca herramienta MCP."""
import json
import re
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator
from petroandes.contracts.common import Contract, Scope, Sha256, Text, Use
from petroandes.paths import APP_ROOT, relative_path
from petroandes.index.common import digest, file_digest


class ApprovalSpec(Contract):
    doc_id: Text
    version_documental: Text | None
    rol_area_simulado: Text
    usos: tuple[Use, ...] = Field(min_length=1)
    restricciones: tuple[Text, ...] = Field(min_length=1)


class Authorization(Contract):
    base: Literal["app"]
    path: Text
    sha256: Sha256


class ApprovalRequest(Contract):
    request_id: Text
    perfil: Literal["laboratorio"]
    simulacion_academica: Literal[True]
    revisor_humano: Text
    autorizacion: Authorization
    ambito: Scope
    grupos: tuple[Text, ...] = Field(min_length=1)
    effective_to: AwareDatetime
    expected_revision: int = Field(strict=True, ge=0)
    documentos: tuple[ApprovalSpec, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def no_placeholders_or_duplicates(self):
        def check(value):
            if isinstance(value, str) and re.search(
                    r"\b(TODO|PLACEHOLDER|PENDIENTE|TBD|REEMPLAZAR|SIN_DEFINIR)\b", value, re.I):
                raise ValueError("Campo administrativo sin resolver")
            if isinstance(value, dict):
                for item in value.values():
                    check(item)
            if isinstance(value, list):
                for item in value:
                    check(item)
        check(self.model_dump(mode="json"))
        keys = [(item.doc_id, item.version_documental) for item in self.documentos]
        if len(keys) != len(set(keys)) or len(self.grupos) != len(set(self.grupos)):
            raise ValueError("Identidades o grupos duplicados")
        for spec in self.documentos:
            if len(spec.usos) != len(set(spec.usos)):
                raise ValueError("Usos duplicados")
        return self


def load_request(path):
    envelope = json.loads(path.read_text(encoding="utf-8"))
    names = envelope.pop("document_files")
    if len(names) != len(set(names)):
        raise ValueError("Fichas administrativas duplicadas")
    envelope["documentos"] = [json.loads(relative_path(name, path.parent).read_text(encoding="utf-8"))
                               for name in names]
    request = ApprovalRequest.model_validate(envelope)
    source = relative_path(request.autorizacion.path, APP_ROOT)
    if file_digest(source) != request.autorizacion.sha256:
        raise ValueError("La evidencia de autorización cambió")
    return request


def request_digest(request):
    return digest(request.model_dump(mode="json"))
