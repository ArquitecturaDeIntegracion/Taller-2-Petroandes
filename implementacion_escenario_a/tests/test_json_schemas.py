"""Prueba esquemas publicados mediante resolución local, sin consultar la red."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "contracts/v0.1.0"


def validator(name):
    resources = []
    for path in SCHEMAS.glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        resources.append((path.as_uri(), Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)
    return Draft202012Validator({"$ref": (SCHEMAS / f"{name}.json").as_uri()},
                                registry=registry)


def test_search_schema_resolves_filters_and_rejects_privileges():
    schema = validator("SearchQuery")
    schema.validate({"consulta": "SINTETICO", "filtros": {"activo": "SINTETICO"}})
    with pytest.raises(ValidationError):
        schema.validate({"consulta": "SINTETICO", "filtros": {"estado": "certificado"}})
    with pytest.raises(ValidationError):
        schema.validate({"consulta": "SINTETICO", "perfil": "laboratorio"})


def test_response_schema_resolves_all_references_locally():
    validator("SearchResponse").validate({"estado": "abstencion",
        "correlation_id": "00000000-0000-4000-8000-000000000001",
        "generation_id": None, "revision_gobierno": 0, "afirmaciones": [],
        "evidencia": [], "motivo_abstencion": "sin_evidencia_autorizada"})
