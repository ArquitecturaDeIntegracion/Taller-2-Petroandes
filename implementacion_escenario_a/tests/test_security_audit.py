"""Auditoría en el límite MCP, privacidad y denegación si no puede persistirse evidencia."""
import asyncio
import json
from contextlib import contextmanager
from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from mcp import types

from petroandes.contracts.common import Scope
from petroandes.governance.models import ServiceContext
from petroandes import mcp_tools
from petroandes.security.audit import AuditReceipt


@contextmanager
def connect():
    context = ServiceContext(identidad='OPERADOR-PRUEBA', grupos=frozenset(['LAB']),
                             ambito=Scope(tipo='general', identificador='LAB'), uso='evidencia_historica')
    yield SimpleNamespace(policy=SimpleNamespace(context=context, clock=lambda: datetime.now(timezone.utc)))


def answer(*_):
    return {'resultado': {'estado': 'abstencion', 'motivo_abstencion': 'evidencia_insuficiente',
            'correlation_id': '00000000-0000-0000-0000-000000000001', 'generation_id': 'prueba',
            'revision_gobierno': 1}, 'traza': {'descartados_seguridad': ['chunk-prueba'],
            'senales_seguridad': {'chunk-prueba': ['sustitucion_instrucciones']}}}


def call(server, arguments):
    async def invoke():
        request = types.CallToolRequest(method='tools/call', params=types.CallToolRequestParams(
            name='buscar_documentos', arguments=arguments))
        return (await server.request_handlers[types.CallToolRequest](request)).root
    return asyncio.run(invoke())


def test_receipt_correlates_result_and_does_not_store_input(tmp_path, monkeypatch):
    monkeypatch.setenv('PETROANDES_AUDIT_DIR', str(tmp_path))
    monkeypatch.setattr(mcp_tools, 'answer', answer)
    result = call(mcp_tools.create_server(connect), {'consulta': 'SECRETO-NO-PERSISTIR', 'top_k': 2})
    assert not result.isError
    receipt = json.loads((tmp_path/(result.structuredContent['correlation_id']+'.json')).read_text())
    assert receipt['estado_registro'] == 'completado'
    assert receipt['capa'] == 'F6_filtro_seguridad'
    assert receipt['descartados_seguridad'] == ['chunk-prueba']
    assert 'SECRETO-NO-PERSISTIR' not in json.dumps(receipt)
    assert 'OPERADOR-PRUEBA' not in json.dumps(receipt)


def test_invalid_call_is_audited_and_cannot_set_context(tmp_path, monkeypatch):
    monkeypatch.setenv('PETROANDES_AUDIT_DIR', str(tmp_path))
    result = call(mcp_tools.create_server(connect), {'consulta': 'prueba', 'perfil': 'administrador'})
    assert result.isError and result.content[0].text == 'parametros_invalidos'
    receipt = json.loads((tmp_path/(result.meta['correlation_id']+'.json')).read_text())
    assert receipt['capa'] == 'contrato_mcp' and 'contexto' not in receipt


@pytest.mark.parametrize('when', ['start', 'finish'])
def test_audit_failure_never_returns_evidence(tmp_path, monkeypatch, when):
    monkeypatch.setattr(mcp_tools, 'answer', answer)
    if when == 'start':
        target = tmp_path/'not-a-directory'
        target.write_text('x')
        monkeypatch.setenv('PETROANDES_AUDIT_DIR', str(target))
    else:
        monkeypatch.setenv('PETROANDES_AUDIT_DIR', str(tmp_path))
        def broken(*_, **__):
            raise OSError('Fallo deliberado del almacenamiento')
        monkeypatch.setattr(AuditReceipt, 'finish', broken)
    result = call(mcp_tools.create_server(connect), {'consulta': 'prueba'})
    assert result.isError and result.content[0].text == 'auditoria_no_disponible'
    assert not result.structuredContent
