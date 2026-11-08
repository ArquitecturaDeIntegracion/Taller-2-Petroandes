"""Laboratorio sintético F5 con gobierno, E5 y Qdrant reales."""
import hashlib
import json
from datetime import timedelta
from uuid import NAMESPACE_URL, uuid5

from petroandes.contracts.documents import Fragment
from petroandes.embeddings.input import passage_input
from petroandes.index.stage import Stage
from f2_helpers import NOW, doc, record


def fixture_stage(store, encoder):
    specs = [
        ("PRO-SEG-009", "v1", "procedimiento", (),
         (("ficha", "Válvula violeta. Bloqueo del paso tras una pérdida de contención."),)),
        ("PRO-SEG-015", "v1", "procedimiento", (),
         (("requisitos", "Verificar ausencia de presión antes de actuar."),
          ("secuencia", "Clausurar el conducto ante una fuga."),
          ("secuencia", "Mantener el paso cerrado hasta confirmar el aislamiento."))),
        ("PRO-SEG-015", "v2", "procedimiento", (),
         (("ficha", "Inventario y serialización de candados de entrenamiento."),)),
        ("RES-CREG-0043-2024", None, "resolucion", (),
         (("ficha", "Control de calidad del muestreo y exactitud de instrumentos."),)),
        ("RES-CREG-0043-2023", None, "resolucion", (),
         (("ficha", "Clasificación de materiales y etiquetado de talleres."),)),
        ("FIC-ACT-P101", "v2", "ficha", ("P-101",),
         (("ficha", "Caracterización de la bomba centrífuga de pruebas."),)),
        ("FIC-ACT-P1010", "v1", "ficha", ("P-1010",),
         (("ficha", "Caracterización de otra bomba de pruebas."),)),
    ]
    records, parents, documents = [], [], {}
    for code, version, kind, tags, sections in specs:
        identity = (code, version)
        document = doc(code, str(identity)).model_copy(update={"version_documental": version, "tipo": kind})
        documents[identity] = document
        revision = store.put_document(document, store.verify_revision())
        expiration = NOW + timedelta(hours=1) if code == "PRO-SEG-009" else NOW + timedelta(days=1)
        store.apply_decision(record(document, revision + 1, effective_to=expiration), revision)
        counts = {}
        for order, (section, text) in enumerate(sections):
            counts[section] = counts.get(section, 0) + 1
            parent_id = str(uuid5(NAMESPACE_URL, str((identity, section))))
            key = str(uuid5(NAMESPACE_URL, str((identity, section, order))))
            input_text = passage_input(document, section, "TRAMO-SINTETICO", text)
            fragment = Fragment(doc_id=code, version_documental=version, pdf_sha256=document.pdf_sha256,
                chunk_id=key, section_id=section, titulo_seccion=section, pagina_inicio=1, pagina_fin=1,
                parte=counts[section], orden=order, parent_id=parent_id, texto=text, parser_version="fixture-1",
                particion="structural-es-1.0.0", bundle="e5small-es-1.0.0",
                tokens_entrada=encoder.tokenizer.count(input_text))
            records.append({"fragment": fragment.model_dump(mode="json"), "embedding_input": input_text,
                "embedding_input_sha256": hashlib.sha256(input_text.encode()).hexdigest(),
                "common_context": [{"section_id": "requisitos"}] if section == "secuencia" else [],
                "metadata": {"documento": document.model_dump(mode="json"), "semantica_observada": {
                    "activo_tags_observados": tags, "tramos_observados": ["TRAMO-SINTETICO"]}}})
            if counts[section] == 1:
                parents.append({"parent_id": parent_id})
    return Stage({"perfil": "laboratorio", "generation_id": "fixture-f5"}, tuple(records), tuple(parents)), documents


def trace(report):
    print(json.dumps(report["traza"], ensure_ascii=True))
