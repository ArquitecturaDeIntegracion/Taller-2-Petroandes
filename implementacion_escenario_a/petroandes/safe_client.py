"""Consumidor dedicado para la sustentación: plan del operador, MCP fijo y salida extractiva."""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

from mcp import StdioServerParameters
from petroandes.paths import APP_ROOT, configured, relative_path
from petroandes.security.consumer import execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request-file', required=True, help='JSON relativo al proyecto con llamadas del operador')
    args = parser.parse_args()
    source = relative_path(args.request_file, APP_ROOT)
    if source.stat().st_size > 65536:
        parser.error('El plan excede 64 KiB')
    data = json.loads(source.read_text(encoding='utf-8-sig'))
    environment = {k: v for k, v in os.environ.items() if k.startswith('PETROANDES_')}
    environment.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
    server = StdioServerParameters(command=sys.executable, args=['-m', 'petroandes.demo'],
                                   cwd=str(APP_ROOT), env=environment)
    root = configured('PETROANDES_F9_OUTPUT_DIR', APP_ROOT / 'reports/portable')
    destination = root / ('cliente-seguro-' + uuid4().hex)
    destination.mkdir(parents=True, exist_ok=False)
    try:
        report = asyncio.run(execute(server, data))
    except Exception as exc:
        report = {'status': 'inconclusive', 'error_tipo': type(exc).__name__, 'respuestas': []}
    for row in report.pop('respuestas'):
        print(row['pantalla'])
        print()
        with (destination / 'respuestas.jsonl').open('a', encoding='utf-8') as output:
            output.write(json.dumps(row, ensure_ascii=True) + '\n')
    report['fecha_utc'] = datetime.now(timezone.utc).isoformat()
    (destination / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'Reporte del cliente: {destination}')
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
