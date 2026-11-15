"""Contraste auxiliar del texto PDF con propiedades y píxeles de su representación."""
from pathlib import Path

from .detection import VERSION, scan_text

MAX_BYTES, MAX_PAGES, MAX_SPANS = 16 * 1024 * 1024, 100, 10000


def inspect_pdf(path):
    """No altera el original ni usa OCR. Un resultado incierto exige revisión."""
    import pymupdf

    if Path(path).stat().st_size > MAX_BYTES:
        raise ValueError('PDF excede el límite de inspección de seguridad')
    pages = []
    with pymupdf.open(path) as pdf:
        if pdf.is_encrypted or not 0 < len(pdf) <= MAX_PAGES:
            raise ValueError('PDF cifrado, vacío o demasiado extenso para la inspección')
        for number, page in enumerate(pdf, 1):
            spans = page.get_texttrace()
            if len(spans) > MAX_SPANS or page.rect.width * page.rect.height > 4000000:
                raise ValueError('Página excede el presupuesto de inspección visual')
            flags, suspicious = set(), []
            if not spans:
                flags.add('pagina_sin_texto_verificable')
            for span in spans:
                text = ''.join(chr(char[0]) for char in span['chars'])
                if not text.strip():
                    continue
                codes = set()
                box = pymupdf.Rect(span['bbox'])
                visible = box & page.rect
                if span['type'] > 1 or span['opacity'] <= .01:
                    codes.add('texto_invisible_pdf')
                if visible.is_empty or visible.get_area() < box.get_area() * .95:
                    codes.add('texto_fuera_de_pagina')
                if span['size'] < 3:
                    codes.add('texto_microscopico')
                if not codes and visible.get_area() > 1:
                    pix = page.get_pixmap(matrix=pymupdf.Matrix(1, 1), clip=visible,
                                          colorspace=pymupdf.csGRAY, alpha=False)
                    pixels = pix.samples
                    if pixels and max(pixels) - min(pixels) < 8:
                        codes.add('texto_sin_contraste_visible')
                if codes:
                    flags.update(codes)
                    flags.update(scan_text(text))
                    suspicious.append({'codigos': sorted(codes), 'caracteres': len(text)})
            pages.append({'pagina': number, 'codigos': sorted(flags),
                          'segmentos_sospechosos': len(suspicious)})
    return {'version': VERSION, 'motor': f'PyMuPDF-{pymupdf.VersionBind}',
            'metodo': 'traza_de_pintado_y_contraste_de_pixeles_sin_ocr', 'paginas': pages}


def fragment_flags(fragment, section_text, review):
    flags = set(scan_text(fragment['texto'])) | set(scan_text(section_text))
    for page in review['paginas']:
        if fragment['pagina_inicio'] <= page['pagina'] <= fragment['pagina_fin']:
            flags.update(page['codigos'])
    return sorted(flags)
