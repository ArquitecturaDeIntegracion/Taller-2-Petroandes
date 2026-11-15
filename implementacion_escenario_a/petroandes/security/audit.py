"""Un recibo durable por llamada MCP; sin consultas, fragmentos, credenciales ni secretos."""
import hashlib
import json
import os
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from petroandes.paths import APP_ROOT, configured
from .detection import VERSION, scan_text


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


class AuditReceipt:
    def __init__(self, tool, arguments):
        self.id = str(uuid4())
        self.started = perf_counter()
        self.directory = configured('PETROANDES_AUDIT_DIR', APP_ROOT / 'reports/portable/mcp-audit')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / (self.id + '.json')
        self.data = {'schema_version': 'mcp-audit-1', 'correlation_id': self.id,
                     'iniciado_utc': datetime.now(timezone.utc).isoformat(), 'estado_registro': 'iniciado',
                     'herramienta': tool if tool in ('buscar_documentos', 'obtener_fragmento') else 'desconocida',
                     'entrada_sha256': digest({'herramienta': tool, 'argumentos': arguments}),
                     'detector_version': VERSION}
        with self.path.open('x', encoding='utf-8') as stream:
            self._write(stream)

    def _write(self, stream):
        json.dump(self.data, stream, ensure_ascii=True, separators=(',', ':'))
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())

    def context(self, service):
        ctx = service.policy.context
        self.data['contexto'] = {'identidad_sha256': digest(ctx.identidad),
                                'grupos_sha256': digest(sorted(ctx.grupos)),
                                'ambito': ctx.ambito.model_dump(mode='json'), 'uso': ctx.uso,
                                'reloj_autorizacion': service.policy.clock().isoformat()}

    def finish(self, decision, *, body=None, trace=None, reason=None):
        body, trace = body or {}, trace or {}
        parts = body.get('evidencia', body.get('partes', []))
        rejected = trace.get('descartados_seguridad', [])
        layer = ('F6_filtro_seguridad' if rejected else 'gobierno' if decision == 'denegado'
                 or body.get('motivo_abstencion') == 'sin_evidencia_autorizada' else
                 'contrato_mcp' if reason else 'compositor' if decision == 'abstencion' else 'lectura_mcp')
        self.data.update({'estado_registro': 'completado', 'decision': decision, 'capa': layer,
                          'motivo': reason or body.get('motivo_abstencion') or body.get('error'),
                          'revision_gobierno': body.get('revision_gobierno'),
                          'generation_id': body.get('generation_id'),
                          'descartados_seguridad': rejected,
                          'senales_seguridad': trace.get('senales_seguridad', {}),
                          'salida_sha256': digest(body),
                          'fragmentos': [{'chunk_id': p['chunk_id'], 'doc_id': p['doc_id'],
                                         'pdf_sha256': p['pdf_sha256'], 'section_id': p['section_id'],
                                         'senales_contenido': scan_text(p['texto'])} for p in parts],
                          'duracion_ms': round((perf_counter() - self.started) * 1000, 3)})
        temporary = self.path.with_suffix('.tmp')
        try:
            with temporary.open('x', encoding='utf-8') as stream:
                self._write(stream)
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)
