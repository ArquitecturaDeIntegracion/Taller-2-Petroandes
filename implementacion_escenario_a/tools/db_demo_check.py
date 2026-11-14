"""Comprueba consultas reales y coherencia entre las tres proyecciones de sustentación."""
import argparse
import json
import sys
from contextlib import closing
from pathlib import Path

from project_paths import APP_ROOT
from db_demo_common import load, readonly, workspace_path
from f0_common import write_report
from petroandes.index.common import file_digest
from record_command import record


def exercise(destination):
    from qdrant_client import QdrantClient
    from petroandes.demo import configuration
    _, source, _, _ = configuration()
    before = file_digest(source)
    workspace = destination / 'datos'

    def call(label, operation, *arguments, expected=0):
        command = [sys.executable, str(APP_ROOT / 'tools/db_demo.py'), operation, *map(str, arguments)]
        receipt, stdout, _ = record(command, destination / label, timeout=300)
        assert receipt['exit_code'] == expected, f'{label}: código inesperado; revisar recibo'
        return json.loads(stdout)

    manifest = call('preparacion', 'preparar', '--output-dir', workspace)
    assert manifest['revision'] == 15
    results = {}
    bases = ('gobierno', 'gobierno', 'publicaciones', 'fragmentos', 'fragmentos', 'lexico')
    names = ('gobierno', 'decisiones', 'publicacion', 'fragmentos', 'anexo', 'lexico')
    for index, (base, name) in enumerate(zip(bases, names), 1):
        results[name] = call(name, 'sql', '--workspace', workspace, '--base', base, '--sql',
                             f'examples/sql-sustentacion/{index:02d}_{name}.sql')
    government = results['gobierno']['filas'][0]
    assert government == {'perfil': 'laboratorio', 'schema_version': 1, 'revision_gobierno': 15,
                          'documentos': 19, 'decisiones': 14, 'eventos': 15}
    decision = results['decisiones']['filas'][0]
    assert decision['revision_decision'] == 12 and decision['estado'] == 'certificado'
    assert decision['simulacion_academica'] == decision['contenido_no_confiable'] == 1
    assert 'evidencia_historica' in json.loads(decision['usos'])
    publication = results['publicacion']['filas'][0]
    assert publication['coleccion_qdrant'] == manifest['collection'] and publication['revision_gobierno'] == 15
    rows = results['fragmentos']['filas']
    assert len(rows) == 14 and sum(row['fragmentos_documento'] for row in rows) == 68
    assert results['lexico']['filas'][0]['fragmentos_lexicos'] == 68
    annex = results['anexo']['filas'][0]
    assert annex['confianza'] == 'untrusted' and annex['contenido_no_confiable'] == 1
    assert 'instrucciones_dirigidas_al_procesador' in json.loads(annex['marcas_seguridad'])
    vector = call('qdrant-anexo', 'qdrant', '--workspace', workspace, '--doc-id', 'COM-PRV-0134',
                  '--section-id', 'anexo-notas-de-integracion', '--vector')
    assert vector['puntos_totales'] == 68 and vector['dimension'] == 384 and vector['distancia'] == 'Cosine'
    assert len(vector['puntos']) == 1
    point = vector['puntos'][0]
    assert point['id'] == annex['chunk_id'] and point['dimension_vector'] == 384
    assert point['payload']['texto'] == annex['texto_integro']
    ranking = call('qdrant-densa', 'qdrant', '--workspace', workspace,
                   '--consulta', 'P-101 presión de diseño', '--top-k', 3)
    assert len(ranking['puntos']) == 3 and all('score' in row for row in ranking['puntos'])
    for label, query in [('escritura-denegada', 'DELETE FROM documents'),
                         ('attach-denegado', "ATTACH DATABASE ':memory:' AS externo")]:
        rejected = call(label, 'sql', '--workspace', workspace, '--base', 'gobierno', '--query', query, expected=1)
        assert rejected['tipo'] == 'DatabaseError' and 'authorized' in rejected['motivo']
    _, files = load(workspace)
    ids = {}
    for base in ('fragmentos', 'lexico'):
        with closing(readonly(files[base])) as db:
            ids[base] = {row['chunk_id'] for row in db.execute('SELECT chunk_id FROM fragments')}
    client = QdrantClient(path=str(files['qdrant']))
    try:
        points, offset = client.scroll(manifest['collection'], limit=128, with_payload=False, with_vectors=False)
    finally:
        client.close()
    assert offset is None and ids['fragmentos'] == ids['lexico'] == {str(point.id) for point in points}
    assert file_digest(source) == before == file_digest(files['gobierno'])
    return {'status': 'passed', 'revision': 15, 'documentos_inventario': 19,
            'documentos_publicados': 14, 'fragmentos_publicados': 68, 'dimension_vector': 384,
            'consultas_sql': 6, 'consultas_qdrant': 2, 'restricciones_sql_comprobadas': 2,
            'anexo_identico_sql_qdrant': True, 'ids_tres_proyecciones_identicos': True,
            'snapshot_original_y_copia_intactos': True, 'snapshot_sha256': before,
            'datos': workspace.relative_to(APP_ROOT).as_posix(),
            'ranking_denso_observado': [{'doc_id': row['payload']['doc_id'],
                 'section_id': row['payload']['section_id'], 'score': row['score']} for row in ranking['puntos']],
            'alcance': 'consulta directa administrativa en copia aislada con reloj histórico; no MCP ni autorización operativa'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    destination = workspace_path(args.output_dir)
    destination.mkdir(parents=True, exist_ok=False)
    try:
        summary = exercise(destination)
    except Exception as exc:
        summary = {'status': 'failed', 'tipo': type(exc).__name__, 'motivo': str(exc)}
    write_report(destination / 'summary.json', summary)
    return int(summary['status'] != 'passed')


if __name__ == '__main__':
    raise SystemExit(main())
