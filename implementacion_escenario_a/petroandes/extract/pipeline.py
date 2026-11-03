"""Procesa el catálogo entero; cada documento se prepara o se rechaza con causa."""
import hashlib
import json
from collections import Counter

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path
from petroandes.chunk.structural import PARTITION, stable_uuid
from petroandes.chunk.context import CONTEXT_POLICY
from petroandes.embeddings.input import E5Tokenizer
from petroandes.paths import APP_ROOT, ARTIFACTS_DIR, PROJECT_ROOT, relative_path
from .metadata import relations_for
from .models import ExtractionReview
from .output import write_document, write_json, write_jsonl
from .pdf import PARSER_VERSION
from .prepare import prepare_document
from .staging import store_generation


def ingest(perfil, output):
    output = APP_ROOT / output
    output.mkdir(parents=True, exist_ok=False)
    tokenizer = E5Tokenizer()
    registry = json.loads((APP_ROOT / "knowledge/sources.json").read_text(encoding="utf-8"))
    pdf_root = relative_path(registry["corpus_pdf"], PROJECT_ROOT)
    md_root = relative_path(registry["corpus_md"], PROJECT_ROOT)
    reports, fragments, parents = [], [], []
    with Catalog.open(profile_path(perfil), perfil, read_only=True) as catalog:
        snapshot = catalog.snapshot()
        actual_files = sorted(pdf_root.rglob("*.pdf"))
        if len(snapshot.documentos) != registry["expected_logical_documents"] or len(actual_files) != 19:
            raise ExtractionReview("Inventario incompleto; no preparar una generación parcial silenciosa")
        for index, document in enumerate(sorted(snapshot.documentos, key=lambda doc: doc.pdf_uri), 1):
            sections, extraction = (), None
            try:
                if not document.pdf_uri.startswith("project:"):
                    raise ExtractionReview("Referencia sin base PDF explícita")
                path = relative_path(document.pdf_uri.removeprefix("project:"), PROJECT_ROOT)
                md = md_root / path.relative_to(pdf_root).with_suffix(".md")
                result = prepare_document(document, path, md, snapshot, relations_for(catalog, document), tokenizer)
                report, children, source_parents, sections, extraction = result
                fragments.extend(children)
                parents.extend(source_parents)
            except (ExtractionReview, OSError, ValueError) as exc:
                report = {"doc_id": document.doc_id, "version_documental": document.version_documental,
                    "pdf_sha256": document.pdf_sha256, "pdf_uri": document.pdf_uri, "tipo": document.tipo,
                    "status": "requiere_revision", "motivo": str(exc), "fragmentos": 0, "publicado": False}
            folder = output / f"document-{index:02d}"
            write_document(folder, report, sections, extraction)
            reports.append({"path": f"{folder.name}/report.json", **report})
        if catalog.verify_revision() != snapshot.revision:
            raise ExtractionReview("Gobierno cambió durante preparación; repetir antes de consolidar")
    identity = {"perfil": perfil, "governance_revision": snapshot.revision,
        "parser_version": PARSER_VERSION, "partition": PARTITION, "tokenizer": tokenizer.config,
        "input_format": "e5passage-es-1.0.0", "context_policy": CONTEXT_POLICY,
        "documents": [(row["doc_id"], row["version_documental"], row["pdf_sha256"], row["status"])
                      for row in reports]}
    manifest = {"evidence_schema_version": 2, "generation_id": stable_uuid(identity),
        "perfil": perfil, "governance_revision": snapshot.revision, "parser_version": PARSER_VERSION,
        "partition": PARTITION, "embedding_bundle": tokenizer.config["bundle"],
        "input_format": "e5passage-es-1.0.0", "context_policy": CONTEXT_POLICY,
        "tokenizer_revision": tokenizer.config["revision"], "tokenizer_sha256": tokenizer.config["tokenizer_sha256"],
        "documentos": len(reports), "preparados": sum(row["status"] == "preparado" for row in reports),
        "rechazados": sum(row["status"] != "preparado" for row in reports), "fragmentos": len(fragments),
        "padres": len(parents), "por_tipo": dict(Counter(row["tipo"] for row in reports)),
        "max_tokens_entrada": max((item["fragment"]["tokens_entrada"] for item in fragments), default=0),
        "publication_state": "staging_no_autorizado", "index_revision": None,
        "document_reports": [row["path"] for row in reports]}
    fragment_files = write_jsonl(output, "fragments", fragments)
    parent_files = write_jsonl(output, "parents", parents)
    # El manifiesto de una generación es independiente del nombre de la corrida de evidencia.
    stage_manifest = {key: value for key, value in manifest.items() if key != "document_reports"}
    stage, reused = store_generation(stage_manifest, fragments, parents)
    manifest.update({"stage_ref": {"base": "artifacts", "path": stage.relative_to(ARTIFACTS_DIR).as_posix()},
        "stage_reused": reused, "fragment_files": fragment_files, "parent_files": parent_files,
        "file_sha256": {name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                        for name in (*fragment_files, *parent_files)}})
    write_json(output / "manifest.json", manifest)
    return manifest
