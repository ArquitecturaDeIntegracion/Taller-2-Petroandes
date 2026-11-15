"""Detección heurística acotada, independiente del documento y de su sección."""
import base64
import re
import unicodedata
from urllib.parse import unquote

VERSION = 'contenido-no-confiable-1.0.0'
PATTERNS = {
    'sustitucion_instrucciones': (
        r'\b(?:ignor\w*|disregard|forget|olvid\w*|omite|omita)\b.{0,90}'
        r'\b(?:instrucciones|instructions|system prompt|operador|previous|anteriores|previas)\b'),
    'suplantacion_rol': r'(?:\[\s*(?:system|developer|sistema)\s*\]|<\|(?:im_start|system|developer)\|>|'
                       r'\byou are now\b|\bactua como (?:sistema|administrador)\b)',
    'ocultacion_al_usuario': r'\b(?:no (?:informe|informes|avise|avises)|do not (?:tell|inform|notify)|'
                            r'don.t tell)\b.{0,45}\b(?:usuario|user|operador)\b',
    'exfiltracion_solicitada': r'\b(?:envia\w*|envi[eo]\w*|remit\w*|send|upload|forward|post)\b'
                             r'.{0,160}(?:https?://|\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b)',
    'orden_al_procesador': r'\b(?:instruccion(?:es)? para (?:sistemas de procesamiento|el (?:agente|modelo))|'
                          r'instructions? for (?:the )?(?:ai|assistant|agent))\b',
}


def normalized(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) not in ('Mn', 'Cf'))
    return re.sub(r'\s+', ' ', text)


def scan_text(text):
    """Señales, no prueba de intención ni detector universal. Nunca ejecuta lo decodificado."""
    if len(text) > 120000:
        return ('contenido_excede_limite_revision',)
    clean = normalized(text)
    flags = {name for name, pattern in PATTERNS.items() if re.search(pattern, clean)}
    if 'orden_al_procesador' in flags:
        flags.add('instrucciones_dirigidas_al_procesador')
    if any(unicodedata.category(c) == 'Cf' for c in text):
        flags.add('unicode_invisible_o_bidi')
    variants = [unquote(text)] if re.search(r'%[0-9a-fA-F]{2}', text) else []
    for token in re.findall(r'(?<![\w+/])[A-Za-z0-9+/]{24,4096}={0,2}(?![\w+/])', text)[:8]:
        try:
            variants.append(base64.b64decode(token, validate=True).decode('utf-8'))
        except (ValueError, UnicodeError):
            continue
    for variant in variants:
        decoded = normalized(variant)
        if any(re.search(pattern, decoded) for pattern in PATTERNS.values()):
            flags.add('instruccion_codificada')
    return tuple(sorted(flags))


def findings(fragment, record):
    """Reescanea el texto y conserva señales verificadas en la ingesta del PDF completo."""
    security = record.get('metadata', {}).get('seguridad', {})
    flags = set(scan_text(fragment.texto))
    if security.get('detector_version') == VERSION:
        flags.update(security.get('security_flags', ()))
    elif security:
        flags.add('indice_requiere_revision_seguridad')
    return tuple(sorted(flags))
