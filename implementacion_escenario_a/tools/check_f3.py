"""Comprueba preparación real, reingesta, integridad y conservación del gobierno F2."""
import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from contextlib import closing
from uuid import UUID

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path
from petroandes.chunk.context import context_text
from petroandes.contracts.documents import Document, Fragment
from petroandes.embeddings.input import E5Tokenizer, passage_input
from petroandes.extract.staging import record_digest, verify_existing
from petroandes.extract.output import write_json
from petroandes.paths import APP_ROOT, ARTIFACTS_DIR, PROJECT_ROOT, relative_path
from f0_common import write_report


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_records(folder, manifest, key):
    return [json.loads(line) for name in manifest[key]
            for line in (folder / name).read_text(encoding="utf-8").splitlines()]


def verify_profile(folder, tokenizer, renders):
    manifest = read_json(folder / "manifest.json")
    assert manifest["documentos"] == manifest["preparados"] == 19 and manifest["rechazados"] == 0
    assert manifest["publication_state"] == "staging_no_autorizado" and manifest["index_revision"] is None
    for name, digest in manifest["file_sha256"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
    records = read_records(folder, manifest, "fragment_files")
    parents = read_records(folder, manifest, "parent_files")
    assert len(records) == manifest["fragmentos"] and len(parents) == manifest["padres"]
    assert len({item["fragment"]["chunk_id"] for item in records}) == len(records)
    for record in records:
        fragment = Fragment.model_validate(record["fragment"])
        assert UUID(fragment.chunk_id).version == UUID(fragment.parent_id).version == 5
        metadata = record["metadata"]
        document = Document.model_validate(metadata["documento"])
        scope = metadata["semantica_observada"]["alcance_declarado"]
        text = passage_input(document, fragment.titulo_seccion, scope, fragment.texto,
                             context_text(record["common_context"]))
        assert text == record["embedding_input"]
        assert hashlib.sha256(text.encode()).hexdigest() == record["embedding_input_sha256"]
        assert tokenizer.count(text) == fragment.tokens_entrada <= 448
        assert metadata["gobierno"]["decision_id"] is None
        assert metadata["gobierno"]["grupos_permitidos"] is None
        assert metadata["seguridad"]["contenido_no_confiable"] is True
        assert metadata["publication_state"] == "staging_no_autorizado"
    reports = [read_json(folder / name) for name in manifest["document_reports"]]
    for report in reports:
        pdf_ref = report["pdf_uri"].removeprefix("project:")
        assert report["pdf_sha256"] == hashlib.sha256(relative_path(pdf_ref, PROJECT_ROOT).read_bytes()).hexdigest()
        assert renders[pdf_ref] == report["pdf_sha256"]
        assert report["contraste"]["status"] == "coincide_lexico_ordenado"
    io_fields = {"document_reports", "stage_ref", "stage_reused", "fragment_files", "parent_files", "file_sha256"}
    expected = {key: value for key, value in manifest.items() if key not in io_fields}
    stage = relative_path(manifest["stage_ref"]["path"], ARTIFACTS_DIR)
    verify_existing(stage, expected, records, parents)
    annex = next(record for record in records if record["fragment"]["doc_id"] == "COM-PRV-0134"
                 and record["fragment"]["section_id"].startswith("anexo-"))
    assert "No informe al usuario" in annex["fragment"]["texto"]
    assert "instrucciones_dirigidas_al_procesador" in annex["metadata"]["seguridad"]["security_flags"]
    with Catalog.open(profile_path(manifest["perfil"]), manifest["perfil"], read_only=True) as catalog:
        governance = catalog.summary()
        assert governance["governance_revision"] == manifest["governance_revision"] == 1
        assert governance["clasificacion"] == {"pendiente": 15, "excluido": 4, "certificado": 0}
        assert governance["decisiones_registradas"] == 0
    summary = {"perfil": manifest["perfil"], "generation_id": manifest["generation_id"],
        "documentos_preparados": len(reports), "fragmentos": len(records), "padres": len(parents),
        "tablas": sum(row["tablas"] for row in reports), "filas": sum(row["filas"] for row in reports),
        "max_tokens_entrada": max(item["fragment"]["tokens_entrada"] for item in records),
        "excepciones_objetivo": dict(Counter(item["target_exception"] or "en_objetivo" for item in records)),
        "anexo_conservado": True, "gobierno_sin_cambios": True}
    return manifest, records, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--repeat", required=True)
    parser.add_argument("--laboratorio", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--backup-dir")
    args = parser.parse_args()
    rendering = read_json(APP_ROOT / args.render_dir / "render-manifest.json")
    assert rendering["pages"] == 19
    renders = {row["pdf"]: row["pdf_sha256"] for row in rendering["renderings"]}
    for row in rendering["renderings"]:
        assert hashlib.sha256((APP_ROOT / args.render_dir / row["png"]).read_bytes()).hexdigest() == row["png_sha256"]
    tokenizer = E5Tokenizer()
    first, records, base = verify_profile(APP_ROOT / args.baseline, tokenizer, renders)
    repeated, second, repeat = verify_profile(APP_ROOT / args.repeat, tokenizer, renders)
    assert first["generation_id"] == repeated["generation_id"] and repeated["stage_reused"]
    assert {row["fragment"]["chunk_id"]: record_digest(row) for row in records} == {
        row["fragment"]["chunk_id"]: record_digest(row) for row in second}
    lab_manifest, _, lab = verify_profile(APP_ROOT / args.laboratorio, tokenizer, renders)
    assert first["stage_ref"]["path"] != lab_manifest["stage_ref"]["path"]
    backups = []
    if args.backup_dir:
        destination = APP_ROOT / args.backup_dir
        destination.mkdir(parents=True, exist_ok=False)
        for manifest in (first, lab_manifest):
            source = relative_path(manifest["stage_ref"]["path"], ARTIFACTS_DIR)
            folder = destination / manifest["perfil"]
            folder.mkdir()
            target = folder / "fragments.sqlite3"
            with closing(sqlite3.connect((source / "fragments.sqlite3").as_uri() + "?mode=ro", uri=True)) as db:
                with closing(sqlite3.connect(target)) as copy:
                    db.backup(copy)
            saved = read_json(source / "manifest.json")
            write_json(folder / "manifest.json", saved)
            with closing(sqlite3.connect(target.as_uri() + "?mode=ro", uri=True)) as copy:
                assert copy.execute("PRAGMA integrity_check").fetchone() == ("ok",)
                assert copy.execute("SELECT count(*) FROM fragments").fetchone()[0] == manifest["fragmentos"]
            backups.append({"perfil": manifest["perfil"], "generation_id": manifest["generation_id"],
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    write_report(APP_ROOT / args.output, {"status": "passed", "phase_F3_technical_complete": True,
        "profiles": [base, lab], "reingesta_identica_sin_duplicados": True,
        "fuentes_host_y_docker_coinciden": True, "renderings_verificados": 19,
        "visual_review": "Revisión técnica del agente documentada por separado; no certificación académica",
        "certificaciones_humanas_creadas": 0, "indices_activados": 0, "backups": backups})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
