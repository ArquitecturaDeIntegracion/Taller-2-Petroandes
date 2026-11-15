"""F9.2: exposición por MCP real, consumidor dedicado, detector PDF y auditoría por llamada."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from mcp import StdioServerParameters
from f0_common import configure_cache, write_report
from f7_inspector_client import Inspector, server_entry
from f9_content_prepare import prepare, NOW
from petroandes.catalog.api import Catalog
from petroandes.contracts.queries import SearchQuery
from petroandes.governance.eligibility import EligibilityService
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT
from petroandes.retrieve import Retriever
from petroandes.security.consumer import execute
from petroandes.security.detection import findings


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True) + '\n', encoding='utf-8')


def run(workspace, destination):
    cases, config, records, publication, encoder, context = prepare(workspace)
    save(destination/'casos.json', {'tipo': 'sinteticos_nuevos_sin_reserva', 'casos': cases})
    fixtures = destination/'pdf-sinteticos'
    fixtures.mkdir()
    for case in cases:
        source = workspace/'corpus/05_comunicaciones'/f'{case["doc_id"]}.pdf'
        copyfile(source, fixtures/f'{case["id"]}.pdf')
    save(destination/'senales-ingesta.json', [{'chunk_id': r['fragment']['chunk_id'],
         'doc_id': r['fragment']['doc_id'], 'section_id': r['fragment']['section_id'],
         'seguridad': r['metadata']['seguridad']} for r in records])
    catalog_path = workspace/'catalog.sqlite3'
    before = file_digest(catalog_path)
    audit_dir = destination/'mcp-audit'
    audit_dir.mkdir()
    args = [str(APP_ROOT/'tests/f7_stdio_fixture.py'), str(config)]
    environment = server_entry(sys.executable, args, PETROANDES_AUDIT_DIR=str(audit_dir))['env']
    server = StdioServerParameters(command=sys.executable, args=args, cwd=str(APP_ROOT), env=environment)
    requests, raw = [], {}
    with Catalog.open(catalog_path, 'laboratorio', read_only=True) as catalog:
        service = Retriever(workspace/'index', EligibilityService(catalog, context, clock=lambda: NOW), encoder)
        for case in cases:
            # Diez candidatos permiten observar el ancla del control con cinco secciones.
            # No se modifica RRF: la corrida inicial con top_k=5 se conserva como hallazgo.
            query = {'consulta': f'Recomendación de {case["doc_id"]}.', 'top_k': 10}
            raw[case['id']] = service.search(SearchQuery.model_validate(query))
            save(destination/f'{case["id"]}-recuperacion.json', raw[case['id']])
            requests.extend([{'herramienta': 'obtener_fragmento', 'argumentos': {
                'doc_id': case['doc_id'], 'version_documental': '1', 'section_id': 'recomendacion'}},
                {'herramienta': 'buscar_documentos', 'argumentos': query}])
    calls = []
    batch_checks = []
    for offset in range(0, len(requests), 10):
        batch = asyncio.run(execute(server, {'llamadas': requests[offset:offset+10]}))
        save(destination/f'cliente-{offset//10+1}.json', batch)
        batch_checks.append(batch['status'] == 'passed' and batch['llamadas_planificadas'] == batch['llamadas_ejecutadas'])
        calls.extend(batch['respuestas'])
    results = []
    for index, case in enumerate(cases):
        direct, search = calls[index*2:index*2+2]
        part = next(r for r in records if r['fragment']['doc_id'] == case['doc_id']
                    and r['fragment']['section_id'] == 'recomendacion')
        chunk = part['fragment']['chunk_id']
        receipt = json.loads((audit_dir/(search['resultado']['correlation_id']+'.json')).read_text())
        retrieved = any(p['chunk_id'] == chunk for p in raw[case['id']]['resultado'].get('evidencia', []))
        exposed = any(p['chunk_id'] == chunk and p['texto'] == part['fragment']['texto']
                      for p in direct['resultado'].get('partes', []))
        detected = bool(part['metadata']['seguridad']['security_flags'])
        checks = {'recuperado': retrieved, 'expuesto_literal_cliente': exposed,
                  'deteccion_esperada': detected == case['malicioso'],
                  'resultado_esperado': search['resultado']['estado'] == ('abstencion' if case['malicioso'] else 'respondida'),
                  'auditoria_completa': receipt['estado_registro'] == 'completado',
                  'capa_evidenciada': chunk in receipt['descartados_seguridad'] if case['malicioso']
                                      else chunk not in receipt['descartados_seguridad']}
        results.append({'id': case['id'], 'malicioso': case['malicioso'], 'detectado': detected,
                        'status': 'passed' if all(checks.values()) else 'failed', 'checks': checks})
    # Un anexo benigno no recibe una marca por su nombre.
    from petroandes.contracts.documents import Fragment
    benign_annex = [r for r in records if r['fragment']['section_id'].startswith('anexo-')]
    annex_ok = bool(benign_annex) and all(not findings(Fragment.model_validate(r['fragment']), r) for r in benign_annex)
    # Inspector independiente verifica la misma interfaz y el rechazo de autoautorización.
    inspector = Inspector(workspace, destination/'inspector')
    inspector.destination.mkdir()
    inspector.configure({'historico': server_entry(sys.executable, args, PETROANDES_AUDIT_DIR=str(audit_dir))})
    listed, _ = inspector.run('list', 'historico')
    attack, _ = inspector.run('ataque', 'historico', tool='buscar_documentos', arguments=requests[1]['argumentos'])
    invalid, _ = inspector.run('autoautorizacion', 'historico', tool='buscar_documentos',
                              arguments=requests[1]['argumentos'] | {'grupos': ['ADMIN']}, expected_exit=5)
    receipts = [json.loads(p.read_text()) for p in audit_dir.glob('*.json')]
    integrity = before == file_digest(catalog_path)
    checks = {'planes_invariables': all(batch_checks), 'anexo_benigno_sin_marca': annex_ok,
              'mcp_solo_dos_lecturas': {t['name'] for t in listed['tools']} == {'buscar_documentos', 'obtener_fragmento'},
              'inspector_abstencion': attack['structuredContent']['estado'] == 'abstencion',
              'autoautorizacion_rechazada': invalid.get('isError') is True and invalid['content'][0]['text'] == 'parametros_invalidos',
              'catalogo_intacto': integrity, 'auditoria_por_llamada': len(receipts) == len(requests)+2,
              'sin_registros_incompletos': all(r['estado_registro'] == 'completado' for r in receipts),
              'sin_texto_en_auditoria': all(case['texto'] not in json.dumps(receipts, ensure_ascii=False) for case in cases)}
    save(destination/'resultados.json', results)
    return {'status': 'passed' if all(checks.values()) and all(r['status'] == 'passed' for r in results) else 'failed',
            'version_arnes': 'F9.2', 'checks': checks, 'casos_pdf': len(results),
            'adversariales': sum(r['malicioso'] for r in results), 'benignos': sum(not r['malicioso'] for r in results),
            'detectados_adversariales': sum(r['malicioso'] and r['detectado'] for r in results),
            'falsos_positivos_benignos': sum(not r['malicioso'] and r['detectado'] for r in results),
            'llamadas_cliente': len(calls), 'registros_auditoria': len(receipts), 'top_k_ensayo': 10,
            'publicacion': publication,
            'llm_real': 'no_evaluado', 'reserva_ejecutada': False,
            'limites': ['Cliente sin LLM; no acredita resistencia semántica de Copilot.',
                       'Detección por señales y contraste visual sin OCR; cobertura finita.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    destination = (APP_ROOT/parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    try:
        configure_cache(offline=True)
        with TemporaryDirectory(prefix='f9-2-pdf-') as directory:
            summary = run(Path(directory), destination)
    except Exception as exc:
        summary = {'status': 'inconclusive', 'error_tipo': type(exc).__name__, 'motivo': str(exc)}
    write_report(destination/'summary.json', summary)
    return 0 if summary['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
