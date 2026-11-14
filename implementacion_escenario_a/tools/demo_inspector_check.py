"""Comprueba la conexión única con el MCP Inspector real fijado por el proyecto."""
import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from f7_inspector_client import Inspector, server_entry
from f0_common import write_report
from project_paths import APP_ROOT
from petroandes.contracts.responses import FragmentResponse, SearchResponse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    destination = (APP_ROOT / parser.parse_args().output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    cases = json.loads((APP_ROOT / 'config/demo-pruebas.json').read_text(encoding='utf-8'))['casos']
    checked = []
    with TemporaryDirectory(prefix='petroandes-inspector-demo-') as directory:
        inspector = Inspector(Path(directory), destination)
        inspector.configure({'petroandes': server_entry(sys.executable, ['-m', 'petroandes.demo'])})
        listed, _ = inspector.run('listado', 'petroandes')
        assert {tool['name'] for tool in listed['tools']} == {'buscar_documentos', 'obtener_fragmento'}
        for case in (cases[0], cases[3], cases[7]):
            result, _ = inspector.run(case['id'], 'petroandes', tool=case['herramienta'],
                                      arguments=case['argumentos'])
            assert not result.get('isError')
            body = result['structuredContent']
            model = SearchResponse if case['herramienta'] == 'buscar_documentos' else FragmentResponse
            model.model_validate(body)
            assert body['estado'] == case['estado'] and body['revision_gobierno'] == 15
            for field in ('error', 'motivo_abstencion'):
                if field in case:
                    assert body[field] == case[field]
            assert all(value in json.dumps(body, ensure_ascii=False) for value in case.get('literales', ()))
            checked.append({'id': case['id'], 'estado': body['estado']})
        write_report(destination / 'summary.json', {'status': 'passed', 'inspector': inspector.version,
                     'servidor': 'petroandes', 'revision': 15, 'comprobaciones': checked,
                     'evaluacion_formal_ejecutada': False})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
