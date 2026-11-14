"""Copia de sustentación y conexiones SQLite de solo lectura, sin tocar el MCP."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from project_paths import APP_ROOT, relative_path


def workspace_path(value):
    target = (APP_ROOT / value).resolve()
    root = (APP_ROOT / 'reports/portable').resolve()
    if target == root or not target.is_relative_to(root):
        raise ValueError('La copia debe estar dentro de reports/portable')
    return target


def readonly(path):
    connection = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA query_only=ON')
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
               sqlite3.SQLITE_RECURSIVE}
    connection.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed
                              else sqlite3.SQLITE_DENY)
    return connection


def prepare(value):
    from petroandes.demo import DemoDeployment, configuration
    from petroandes.embeddings.cache import configure_cache
    configure_cache(offline=True)
    destination = workspace_path(value)
    destination.mkdir(parents=True, exist_ok=False)
    deployment = DemoDeployment(destination)
    deployment.prepare()
    data, _, _, clock = configuration()
    with closing(readonly(deployment.index / 'publications.sqlite3')) as db:
        row = db.execute('SELECT receipt FROM generations JOIN active ON id=generation').fetchone()
    receipt = json.loads(row['receipt'])
    generation = receipt['key']['generation_id']
    folder = deployment.index / 'generations' / generation
    files = {'gobierno': deployment.catalog_path,
             'publicaciones': deployment.index / 'publications.sqlite3',
             'fragmentos': folder / 'catalog.sqlite3', 'lexico': folder / 'lexical.sqlite3',
             'qdrant': deployment.index / 'qdrant'}
    manifest = {'schema_version': 1, 'alcance': 'copia aislada para inspeccion tecnica directa',
                'perfil': 'laboratorio', 'revision': data['revision'],
                'reloj_historico': clock.isoformat(), 'snapshot_sha256': data['snapshot']['sha256'],
                'collection': receipt['collection'], 'generation_id': generation,
                'bundle_fingerprint': receipt['key']['bundle_fingerprint'],
                'paths': {name: path.relative_to(destination).as_posix() for name, path in files.items()}}
    (destination / 'db-demo.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n',
                                             encoding='utf-8', newline='\n')
    return manifest


def load(value):
    destination = workspace_path(value)
    manifest = json.loads((destination / 'db-demo.json').read_text(encoding='utf-8'))
    if manifest['schema_version'] != 1 or manifest['perfil'] != 'laboratorio':
        raise ValueError('Manifiesto de sustentación incompatible')
    files = {name: relative_path(path, destination) for name, path in manifest['paths'].items()}
    if not all(path.exists() for path in files.values()):
        raise FileNotFoundError('La copia quedó incompleta; preparar otra carpeta nueva')
    return manifest, files
