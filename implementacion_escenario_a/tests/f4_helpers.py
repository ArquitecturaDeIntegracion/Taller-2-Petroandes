"""Datos sintéticos exclusivos de pruebas F4, sin validez académica."""
import hashlib
from uuid import NAMESPACE_URL, uuid5

from petroandes.contracts.documents import Fragment
from petroandes.embeddings.input import passage_input
from petroandes.index.stage import Stage
from f2_helpers import catalog, doc, record, policy


def stage_fixture(store, encoder):
    documents = [doc("SINTETICO-A"), doc("SINTETICO-B")]
    for document in documents:
        store.put_document(document, store.verify_revision())
    store.apply_decision(record(documents[0], 3), 2)
    records, parents = [], []
    for document in documents:
        text = f"{document.doc_id}: revisión de código P-101 y resolución 2026."
        parent_id = str(uuid5(NAMESPACE_URL, document.doc_id + "padre"))
        fragment_id = str(uuid5(NAMESPACE_URL, document.doc_id + "fragmento"))
        input_text = passage_input(document, "Ficha sintética", "TRAMO-SINTETICO", text)
        fragment = Fragment(doc_id=document.doc_id, version_documental=None, pdf_sha256=document.pdf_sha256,
            chunk_id=fragment_id, section_id="ficha", titulo_seccion="Ficha sintética", pagina_inicio=1,
            pagina_fin=1, parte=1, orden=0, parent_id=parent_id, texto=text, parser_version="fixture-1",
            particion="structural-es-1.0.0", bundle="e5small-es-1.0.0",
            tokens_entrada=encoder.tokenizer.count(input_text))
        records.append({"fragment": fragment.model_dump(mode="json"), "embedding_input": input_text,
            "embedding_input_sha256": hashlib.sha256(input_text.encode()).hexdigest(),
            "metadata": {"documento": document.model_dump(mode="json")}})
        parents.append({"parent_id": parent_id, "texto": text, "doc_id": document.doc_id})
    return Stage({"perfil": "laboratorio", "generation_id": "staging-sintetico-f4"}, tuple(records), tuple(parents))
