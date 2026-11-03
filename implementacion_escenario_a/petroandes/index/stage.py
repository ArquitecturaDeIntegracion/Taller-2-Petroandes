"""Lee F3 comprobando archivos, SQLite, entradas E5 y PDF originales."""
import hashlib
import json
from dataclasses import dataclass

from petroandes.chunk.context import context_text
from petroandes.contracts.documents import Document, Fragment
from petroandes.embeddings.input import passage_input
from petroandes.extract.staging import verify_existing
from petroandes.paths import ARTIFACTS_DIR, PROJECT_ROOT, relative_path
from .common import IndexUnavailable, file_digest


@dataclass(frozen=True)
class Stage:
    manifest: dict
    records: tuple
    parents: tuple


def load_stage(manifest_path, tokenizer):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    config = tokenizer.config
    if (manifest["rechazados"] or manifest["preparados"] != manifest["documentos"]
            or manifest["embedding_bundle"] != config["bundle"]
            or manifest["tokenizer_revision"] != config["revision"]
            or manifest["partition"] != "structural-es-1.0.0"
            or manifest["publication_state"] != "staging_no_autorizado"):
        raise IndexUnavailable("Staging incompleto o incompatible")
    folder = manifest_path.parent
    if not set(manifest["fragment_files"] + manifest["parent_files"]).issubset(manifest["file_sha256"]):
        raise IndexUnavailable("Archivo F3 sin hash en manifiesto")
    for name, expected in manifest["file_sha256"].items():
        if file_digest(relative_path(name, folder)) != expected:
            raise IndexUnavailable("Archivo F3 alterado")
    def read(key):
        return tuple(json.loads(line) for name in manifest[key]
                     for line in relative_path(name, folder).read_text(encoding="utf-8").splitlines())
    records, parents = read("fragment_files"), read("parent_files")
    if len(records) != manifest["fragmentos"] or len(parents) != manifest["padres"]:
        raise IndexUnavailable("Conteos F3 incompatibles")
    verified = set()
    for item in records:
        fragment = Fragment.model_validate(item["fragment"])
        document = Document.model_validate(item["metadata"]["documento"])
        if any(getattr(fragment, key) != getattr(document, key)
               for key in ("doc_id", "version_documental", "pdf_sha256")):
            raise IndexUnavailable("Identidad fragmento/documento distinta")
        source = document.pdf_uri
        if (source, document.pdf_sha256) not in verified:
            if not source.startswith("project:") or file_digest(relative_path(
                    source.removeprefix("project:"), PROJECT_ROOT)) != document.pdf_sha256:
                raise IndexUnavailable("PDF original cambió; reingerir antes de publicar")
            verified.add((source, document.pdf_sha256))
        scope = item["metadata"]["semantica_observada"]["alcance_declarado"]
        text = passage_input(document, fragment.titulo_seccion, scope, fragment.texto,
                             context_text(item["common_context"]))
        if (text != item["embedding_input"] or hashlib.sha256(text.encode()).hexdigest()
                != item["embedding_input_sha256"] or tokenizer.count(text) != fragment.tokens_entrada):
            raise IndexUnavailable("Entrada E5 no coincide con F3")
    ignored = {"document_reports", "stage_ref", "stage_reused", "fragment_files", "parent_files", "file_sha256"}
    if manifest["stage_ref"]["base"] != "artifacts":
        raise IndexUnavailable("Base de staging desconocida")
    verify_existing(relative_path(manifest["stage_ref"]["path"], ARTIFACTS_DIR),
                    {key: value for key, value in manifest.items() if key not in ignored}, records, parents)
    return Stage(manifest, records, parents)
