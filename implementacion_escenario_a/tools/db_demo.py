"""Consultas directas SQLite y Qdrant sobre una copia de sustentación reproducible."""
import argparse
import json
import sqlite3
from contextlib import closing

from project_paths import APP_ROOT, relative_path
from db_demo_common import load, prepare, readonly


def sql(args):
    manifest, files = load(args.workspace)
    query = (relative_path(args.sql, APP_ROOT).read_text(encoding='utf-8') if args.sql
             else args.query)
    with closing(readonly(files[args.base])) as db:
        rows = [dict(row) for row in db.execute(query)]
    return {'motor': 'SQLite', 'base': args.base, 'revision_copia': manifest['revision'],
            'sql': query, 'filas': rows, 'total_filas': len(rows)}


def point_data(point, vector=False):
    data = {'id': str(point.id), 'payload': point.payload}
    if hasattr(point, 'score'):
        data['score'] = point.score
    if vector:
        data['dimension_vector'] = len(point.vector)
        data['primeras_8_coordenadas'] = point.vector[:8]
    return data


def qdrant(args):
    from qdrant_client import QdrantClient, models
    manifest, files = load(args.workspace)
    client = QdrantClient(path=str(files['qdrant']))
    try:
        collection = manifest['collection']
        info = client.get_collection(collection)
        conditions = [models.FieldCondition(key=key, match=models.MatchValue(value=value))
                      for key, value in (('doc_id', args.doc_id), ('section_id', args.section_id)) if value]
        query_filter = models.Filter(must=conditions) if conditions else None
        if args.consulta:
            from petroandes.embeddings.cache import configure_cache
            from petroandes.embeddings.encoder import E5Encoder
            configure_cache(offline=True)
            encoder = E5Encoder()
            vector = encoder.query(args.consulta, expected_fingerprint=manifest['bundle_fingerprint']).vector
            points = client.query_points(collection, query=vector.tolist(), query_filter=query_filter,
                                         limit=args.top_k, with_payload=True, with_vectors=args.vector).points
            next_offset = None
        else:
            points, next_offset = client.scroll(collection, scroll_filter=query_filter, limit=args.top_k,
                                                with_payload=True, with_vectors=args.vector)
        return {'motor': 'Qdrant local', 'collection': collection, 'generation_id': manifest['generation_id'],
                'revision_copia': manifest['revision'], 'puntos_totales': client.count(collection, exact=True).count,
                'dimension': info.config.params.vectors.size, 'distancia': info.config.params.vectors.distance.value,
                'consulta': args.consulta, 'filtros': {'doc_id': args.doc_id, 'section_id': args.section_id},
                'modo': 'busqueda_densa_directa' if args.consulta else 'scroll_directo',
                'limite': args.top_k, 'siguiente_offset': str(next_offset) if next_offset else None,
                'puntos': [point_data(point, args.vector) for point in points],
                'alcance': 'Inspeccion administrativa; no aplica permisos de Retriever ni composicion F6'}
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operations = parser.add_subparsers(dest='operation', required=True)
    preparation = operations.add_parser('preparar')
    preparation.add_argument('--output-dir', required=True)
    query = operations.add_parser('sql')
    query.add_argument('--workspace', required=True)
    query.add_argument('--base', choices=('gobierno', 'publicaciones', 'fragmentos', 'lexico'), required=True)
    source = query.add_mutually_exclusive_group(required=True)
    source.add_argument('--sql', help='Archivo relativo al proyecto, con una consulta SELECT')
    source.add_argument('--query', help='Una consulta SELECT; no se admiten escrituras ni ATTACH')
    vectors = operations.add_parser('qdrant')
    vectors.add_argument('--workspace', required=True)
    vectors.add_argument('--doc-id')
    vectors.add_argument('--section-id')
    vectors.add_argument('--vector', action='store_true', help='Muestra dimensión y ocho coordenadas')
    vectors.add_argument('--consulta', help='Consulta semántica directa con el bundle E5 del proyecto')
    vectors.add_argument('--top-k', type=int, default=3)
    args = parser.parse_args()
    if args.operation == 'qdrant' and not 1 <= args.top_k <= 20:
        parser.error('top-k debe estar entre 1 y 20')
    try:
        result = prepare(args.output_dir) if args.operation == 'preparar' else (
            sql(args) if args.operation == 'sql' else qdrant(args))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, RuntimeError, ValueError, KeyError, sqlite3.Error) as exc:
        print(json.dumps({'status': 'failed', 'tipo': type(exc).__name__, 'motivo': str(exc)}, ensure_ascii=False))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
