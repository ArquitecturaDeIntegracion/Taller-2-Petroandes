"""Inspecciona un PDF local desconocido sin publicarlo ni otorgarle permisos."""
import argparse
import json
from hashlib import sha256
from pathlib import Path

from pypdf import PdfReader
from project_paths import APP_ROOT
from petroandes.paths import configured
from petroandes.security.detection import VERSION, scan_text
from petroandes.security.pdf_review import inspect_pdf


def review(path):
    visual = inspect_pdf(path)
    reader = PdfReader(path, strict=True)
    pages = []
    for number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        signals = sorted(set(scan_text(text)) | set(visual['paginas'][number-1]['codigos']))
        pages.append({'pagina': number, 'senales': signals,
                      'texto_sha256': sha256(text.encode()).hexdigest(), 'caracteres': len(text)})
    return {'status': 'requiere_revision' if any(p['senales'] for p in pages) else 'sin_senales_observadas',
            'detector_version': VERSION, 'pdf_sha256': sha256(path.read_bytes()).hexdigest(),
            'paginas': pages, 'metodo_visual': visual['metodo'],
            'publicado': False, 'permisos_otorgados': False,
            'limite': 'Ausencia de señales no certifica seguridad. Sin OCR ni detección universal.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    destination = (APP_ROOT/args.output_dir).resolve()
    root = configured('PETROANDES_F9_OUTPUT_DIR', APP_ROOT/'reports/portable').resolve()
    if not destination.is_relative_to(root) or destination == root:
        parser.error('La salida debe estar dentro del directorio autorizado de reportes')
    destination.mkdir(parents=True, exist_ok=False)
    try:
        report = review((APP_ROOT/args.pdf).resolve())
    except Exception as exc:
        report = {'status': 'inconclusive', 'error_tipo': type(exc).__name__, 'publicado': False}
    (destination/'summary.json').write_text(json.dumps(report, ensure_ascii=True)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    return 1 if report['status'] == 'inconclusive' else 0


if __name__ == '__main__':
    raise SystemExit(main())
