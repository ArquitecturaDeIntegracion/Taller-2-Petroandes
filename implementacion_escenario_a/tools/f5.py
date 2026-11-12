"""Consulta local. El operador selecciona el despliegue, con contexto fijo F4."""
import argparse
import json
import sys
from uuid import UUID

from pydantic import ValidationError

import project_paths  # Carga las raíces también al ejecutar el script desde otra carpeta.
from petroandes.catalog.store import CatalogUnavailable
from petroandes.compose import answer
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.deployment import LocalDeployment


def parse_command(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=("baseline", "laboratorio"))
    operations = parser.add_subparsers(dest="operation", required=True)

    for name, help_text in (("buscar", "Recupera candidatos F5"), ("responder", "Compone extractos citados F6")):
        search = operations.add_parser(name, help=help_text, argument_default=argparse.SUPPRESS)
        search.add_argument("query", nargs="?", help="Objeto JSON conforme al contrato F1")
        search.add_argument("--consulta")
        search.add_argument("--top-k", type=int)
        search.add_argument("--tipo")
        search.add_argument("--activo")
        search.add_argument("--tramo")

    direct = operations.add_parser("obtener", argument_default=argparse.SUPPRESS)
    direct.add_argument("query", nargs="?", help="Objeto JSON conforme al contrato F1")
    direct.add_argument("--doc-id")
    version = direct.add_mutually_exclusive_group()
    version.add_argument("--version", dest="version_documental")
    version.add_argument("--sin-version", dest="version_documental", action="store_const", const=None)
    direct.add_argument("--seccion", dest="section_id")
    direct.add_argument("--parte", type=int)
    direct.add_argument("--pdf-sha256")

    operations.add_parser("expandir").add_argument("chunk_id", type=UUID)
    fields = vars(parser.parse_args(argv))
    profile, operation = fields.pop("profile"), fields.pop("operation")
    if operation == "expandir":
        return profile, operation, str(fields["chunk_id"])

    payload = fields.pop("query", None)
    if payload is not None and fields:
        parser.error("Usa un argumento JSON o las opciones de la operación")
    contract = FragmentQuery if operation == "obtener" else SearchQuery
    if contract is SearchQuery:
        filters = {key: fields.pop(key) for key in ("tipo", "activo", "tramo") if key in fields}
        if filters:
            fields["filtros"] = filters
    try:
        query = contract.model_validate_json(payload) if payload is not None else contract.model_validate(fields)
    except ValidationError as exc:
        errors = exc.errors(include_input=False, include_context=False, include_url=False)
        if any(item["type"] == "json_invalid" for item in errors):
            parser.error(f"JSON no válido. En PowerShell usa las opciones de {operation} --help")
        details = [".".join(map(str, item["loc"])) + " (" + item["msg"] + ")" for item in errors]
        parser.error("Consulta inválida. Revisa " + ", ".join(details))
    return profile, operation, query


def main():
    profile, operation, query = parse_command()
    try:
        with LocalDeployment(profile).connect() as service:
            dispatch = {"buscar": service.search, "obtener": service.obtain, "expandir": service.expand,
                        "responder": lambda request: answer(service, request)}
            report = dispatch[operation](query)
    except (CatalogUnavailable, OSError, RuntimeError, ValueError) as exc:
        print(f"servicio_no_disponible ({type(exc).__name__})", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return int(report["resultado"]["estado"] == "error")


if __name__ == "__main__":
    raise SystemExit(main())
