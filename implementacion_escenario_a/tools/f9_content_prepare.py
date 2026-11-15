"""PDF físicos y publicación aislada con el parser, E5, SQLite y Qdrant de la aplicación."""
import json
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pymupdf
from pytest import MonkeyPatch

from petroandes.catalog.api import Catalog
from petroandes.contracts.common import Scope
from petroandes.contracts.documents import Decision
from petroandes.embeddings.encoder import E5Encoder
from petroandes.extract.prepare import prepare_document
from petroandes.governance import pdf_metadata
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import DecisionRecord, ServiceContext
from petroandes.index.stage import Stage
from petroandes.index.publication import Publisher
from petroandes.retrieve import Retriever
from f9_content_cases import cases

NOW = datetime(2026, 11, 14, 12, tzinfo=timezone.utc)
SCOPE = Scope(tipo='general', identificador='LABORATORIO-F9-2')


def make_pdf(path, code, case):
    """La referencia Markdown procede de la especificación, nunca reemplaza la ingesta PDF."""
    document = pymupdf.open()
    page = document.new_page()
    prefix = ['LABORATORIO F9.2', 'Corpus tecnico sintetico', 'Sin valor operativo', f'Caso {case["id"]}',
              'Código', code, 'Versión', '1', 'Fecha de emisión', '2026-11-14', 'Tipo', 'Comunicacion',
              'Área emisora', 'LAB-F9', 'Activo / alcance', 'LABORATORIO F9.2']
    page.insert_text((45, 35), '\n'.join(prefix), fontsize=10)
    sections = [('Asunto', 'Inspeccion de laboratorio.'), ('Antecedente', 'Ensayo sintetico sin equipos reales.'),
                ('Recomendación', case['texto']), ('Alcance', 'Unicamente laboratorio educativo.')]
    if case['modo'] == 'anexo_benigno':
        sections.append(('Anexo — notas de integración', 'Tabla auxiliar de referencias del laboratorio.'))
    y = 290
    for heading, body in sections:
        # TextWriter conserva los glifos Unicode y el encabezado del anexo.
        title = pymupdf.TextWriter(page.rect)
        title.append((45, y), heading, font=pymupdf.Font('helv'), fontsize=11)
        title.write_text(page)
        y += 20
        target = heading == 'Recomendación'
        mode = 3 if target and case['modo'] == 'invisible' else 0
        color = (1, 1, 1) if target and case['modo'] == 'blanco' else (0, 0, 0)
        text = pymupdf.TextWriter(page.rect)
        font = pymupdf.Font('china-s' if target and case['modo'] == 'unicode' else 'helv')
        for line in textwrap.wrap(body, width=74, break_long_words=False, break_on_hyphens=False):
            text.append((45, y), line, font=font, fontsize=8 if len(line) > 74 else 10)
            y += 15
        text.write_text(page, color=color, render_mode=mode)
        y += 18
    path.parent.mkdir(parents=True, exist_ok=True)
    document.subset_fonts()
    document.save(path)
    document.close()
    md = path.with_suffix('.md')
    md.write_text('\n\n'.join(f'## {heading}\n{body}' for heading, body in sections), encoding='utf-8')
    return md


def prepare(workspace):
    fixture_cases = cases()
    encoder = E5Encoder()
    context = ServiceContext(identidad='CLIENTE-LAB-F9-2', grupos=frozenset(['LAB-F9-2']),
                             ambito=SCOPE, uso='evidencia_historica')
    catalog_path = workspace / 'catalog.sqlite3'
    with Catalog.create(catalog_path, 'laboratorio') as catalog, MonkeyPatch.context() as patch:
        patch.setattr(pdf_metadata, 'PROJECT_ROOT', workspace)
        sources = []
        for index, case in enumerate(fixture_cases, 201):
            code = f'COM-LAB-{index}'
            path = workspace / 'corpus/05_comunicaciones' / (code + '.pdf')
            md = make_pdf(path, code, case)
            doc, _ = pdf_metadata.read_document(path)
            revision = catalog.put_document(doc, catalog.verify_revision())
            decision = Decision(doc_id=doc.doc_id, version_documental=doc.version_documental,
                pdf_sha256=doc.pdf_sha256, decision_id=f'FIXTURE-F9-2-{case["id"]}', perfil='laboratorio',
                simulacion_academica=True, estado='certificado', evidencia=('PDF-SINTETICO-F9-2',),
                autoridad='ROL-FICTICIO', revisor_humano='FIXTURE-TECNICO-NO-REVISION-HUMANA',
                revisado_en=NOW, effective_from=NOW-timedelta(hours=1), effective_to=NOW+timedelta(days=1),
                ambitos=(SCOPE,), usos=('evidencia_historica',), grupos=('LAB-F9-2',), revision_gobierno=revision+1)
            catalog.apply_decision(DecisionRecord(decision=decision, autenticidad='verificada',
                supuesto='Autorizacion exclusivamente tecnica del fixture aislado; no es una decision del corpus'), revision)
            sources.append((doc, path, md))
            case.update(doc_id=code, pdf_sha256=doc.pdf_sha256)
        snapshot = catalog.snapshot()
        records, parents = [], []
        for doc, path, md in sources:
            _, children, parent, _, _ = prepare_document(doc, path, md, snapshot, [], encoder.tokenizer)
            records.extend(children)
            parents.extend(parent)
        source = Stage({'perfil': 'laboratorio', 'generation_id': 'f9-2-pdf-sinteticos'}, tuple(records), tuple(parents))
        policy = EligibilityService(catalog, context, clock=lambda: NOW)
        with Publisher(workspace / 'index', policy, encoder) as publisher:
            receipt = publisher.publish(source)
    config = {'catalog': str(catalog_path), 'index': str(workspace / 'index'),
              'context': context.model_dump(mode='json'), 'at': NOW.isoformat()}
    config_path = workspace / 'server.json'
    config_path.write_text(json.dumps(config), encoding='utf-8')
    return fixture_cases, config_path, records, receipt, encoder, context
