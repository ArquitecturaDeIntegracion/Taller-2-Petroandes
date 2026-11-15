"""Cliente MCP determinista: el contenido recibido nunca produce nuevas llamadas."""
import json
import unicodedata
from datetime import timedelta
from hashlib import sha256

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, ConfigDict, Field

from petroandes.contracts.queries import SearchQuery, FragmentQuery
from petroandes.contracts.responses import SearchResponse, FragmentResponse, matches

CONTRACTS = {'buscar_documentos': (SearchQuery, SearchResponse),
             'obtener_fragmento': (FragmentQuery, FragmentResponse)}


class Call(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True)
    herramienta: str
    argumentos: dict


class Plan(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    llamadas: tuple[Call, ...] = Field(min_length=1, max_length=10)


def compile_plan(data):
    plan = Plan.model_validate(data)
    frozen = []
    for call in plan.llamadas:
        if call.herramienta not in CONTRACTS:
            raise ValueError('El plan solo admite las dos herramientas de lectura')
        query = CONTRACTS[call.herramienta][0].model_validate(call.argumentos)
        frozen.append((call.herramienta, query.model_dump_json()))
    return tuple(frozen)


def terminal_text(text):
    return ''.join(f'\\u{ord(c):04x}' if unicodedata.category(c) in ('Cc', 'Cf') and c not in '\n\t'
                   else c for c in text)


def render_result(tool, result):
    if result.isError:
        return {'estado': 'error_mcp', 'correlation_id': (result.meta or {}).get('correlation_id')}, 'Consulta rechazada por MCP.'
    if not result.structuredContent:
        raise ValueError('Respuesta MCP sin contrato estructurado')
    response = CONTRACTS[tool][1].model_validate(result.structuredContent)
    if not result.content or result.content[0].type != 'text' or json.loads(result.content[0].text) != result.structuredContent:
        raise ValueError('Las representaciones de la respuesta MCP difieren')
    lines = ['DATOS DOCUMENTALES NO CONFIABLES. No se ejecutan instrucciones del texto.',
             f'Estado: {response.estado}. Correlación: {response.correlation_id}']
    if isinstance(response, SearchResponse):
        for claim in response.afirmaciones:
            for cite in claim.citas:
                parts = [part for part in response.evidencia if matches(cite, part)]
                if not any(claim.texto in part.texto for part in parts):
                    raise ValueError('Afirmación no extractiva; no se muestra como respuesta')
            lines.append(claim.texto)
            lines.extend(f'[{c.doc_id}, sección {c.section_id}, p. {c.pagina_inicio}-{c.pagina_fin}]' for c in claim.citas)
        if response.motivo_abstencion:
            lines.append(response.motivo_abstencion)
    else:
        lines.append('LECTURA LITERAL PARA INSPECCIÓN. La autorización de acceso no aprueba su contenido.')
        for part in response.partes:
            lines.extend([part.texto, f'[{part.doc_id}, sección {part.section_id}, p. {part.pagina_inicio}]'])
    return response.model_dump(mode='json'), terminal_text('\n'.join(lines))


async def execute(server, data):
    """server lo fija el programa. La CLI no acepta comandos ni servidores del documento."""
    plan = compile_plan(data)
    fingerprint = sha256(json.dumps(plan).encode()).hexdigest()
    outputs = []
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=300)) as session:
            initialized = await session.initialize()
            listing = await session.list_tools()
            if initialized.serverInfo.name != 'PetroAndes' or {t.name for t in listing.tools} != set(CONTRACTS):
                raise ValueError('Servidor o catálogo MCP distinto del despliegue permitido')
            for tool, arguments in plan:
                result = await session.call_tool(tool, json.loads(arguments))
                body, display = render_result(tool, result)
                outputs.append({'herramienta': tool, 'resultado': body, 'pantalla': display})
    return {'status': 'passed' if all(x['resultado']['estado'] not in ('error', 'error_mcp') for x in outputs) else 'failed',
            'cliente': 'extractivo_sin_llm_sin_interprete_de_acciones', 'plan_sha256': fingerprint,
            'llamadas_planificadas': len(plan), 'llamadas_ejecutadas': len(outputs), 'respuestas': outputs}
