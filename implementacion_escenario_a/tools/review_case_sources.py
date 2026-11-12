"""Contrasta referencias de revisión con los PDF y la copia histórica de gobierno."""
import argparse
import json
import sqlite3
from contextlib import closing
from functools import cache
from hashlib import sha256
from pathlib import Path

from petroandes.extract.output import write_json, write_jsonl
from petroandes.extract.pdf import extract_pdf
from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path

REVIEW = APP_ROOT / "docs/revision"
REGISTRATION = APP_ROOT / "evidence/lab/20261103/registration"
MANUALS = ("D01", "D02", "D03")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


@cache
def pdf(path):
    doc, sections, extraction = extract_pdf(path)
    pages = {s.section_id: {line.page for b in s.blocks for line in b.lines} for s in sections}
    pages["encabezado"] = {1}  # read_document valida el encabezado de la página 1
    return doc, pages, extraction["parser_version"]


def reference(source):
    path = relative_path(source["path"], PROJECT_ROOT)
    if source["base"] != "project" or not path.is_relative_to(PROJECT_ROOT / "corpus/pdf"):
        raise ValueError(f"Referencia fuera del corpus: {source['path']}")
    doc, pages, _ = pdf(path)
    for field in ("doc_id", "version_documental", "pdf_sha256"):
        if getattr(doc, field) != source[field]:
            raise ValueError(f"{path.name}: {field} no coincide")
    if source["pagina"] not in pages.get(source["section_id"], set()):
        raise ValueError(f"{path.name}: sección/página inválida {source['section_id']}")
    return {key: source[key] for key in
            ("doc_id", "version_documental", "pdf_sha256", "pagina", "section_id")}


def archived_authority(proposals, cases):
    path = REGISTRATION / "laboratorio-after.sqlite3"
    expected = load(REGISTRATION / "summary.json")["backup_sha256"][path.name]
    if digest(path) != expected:
        raise ValueError("La copia de gobierno no coincide con la huella archivada")
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)) as db:
        profile, revision = db.execute("SELECT perfil, revision FROM metadata").fetchone()
        decisions = [json.loads(row[0])["decision"] for row in
                     db.execute("SELECT payload FROM decisions ORDER BY revision")]
    latest = {(item["doc_id"], item["version_documental"]): item for item in decisions}
    certified = {(doc, ver, item["pdf_sha256"]) for (doc, ver), item in latest.items()
                 if item["estado"] == "certificado"}

    def has_certificate(key):
        ref = proposals[key]["documento"]["pdf"]
        return (ref["doc_id"], ref["version_documental"], ref["pdf_sha256"]) in certified

    return {"perfil": profile, "revision": revision, "copia_sha256": expected,
            "certificados": len(certified),
            "manuales_sin_certificado": [key for key in MANUALS if not has_certificate(key)],
            "dependencias_faltantes": {case["case_id"]: missing for case in cases if
                (missing := [key for key in case["precondiciones"]["propuestas_documentales_requeridas"]
                             if not has_certificate(key)])},
            "usos_com_prv_0134": latest[("COM-PRV-0134", None)]["usos"]}


def audit():
    manifest = load(REVIEW / "manifest.json")
    refs = manifest["decision_refs"] + manifest["case_refs"]
    if len(refs) != len(set(refs)) or set(refs) != set(manifest["sha256_fichas_propuestas"]):
        raise ValueError("El manifiesto no enumera las mismas fichas que su lista de huellas")
    data = {}
    for ref in refs:
        path = relative_path(ref, REVIEW)
        if digest(path) != manifest["sha256_fichas_propuestas"][ref]:
            raise ValueError(f"Ficha modificada respecto al manifiesto: {ref}")
        data[ref] = load(path)
    proposals = {data[ref]["id"]: data[ref] for ref in manifest["decision_refs"]}
    cases = [data[ref] for ref in manifest["case_refs"]]
    rows = []
    for case in cases:
        oracle = case["oracle_propuesto"]
        sources = oracle["fuentes_para_revision_humana"] + oracle["evidencia_a_recuperar_y_citar"]
        rows.append({"id": case["case_id"], "referencias": [reference(s) for s in sources]})
    for key in MANUALS:
        item = proposals[key]
        sources = [item["documento"]["pdf"]] + item["evidencia_corpus"]["fuentes"]
        doc, _, _ = pdf(relative_path(sources[0]["path"], PROJECT_ROOT))
        if doc.emisor != item["documento"]["emisor_segun_pdf"]:
            raise ValueError(f"Emisor del encabezado no coincide: {key}")
        rows.append({"id": key, "emisor_segun_pdf": doc.emisor,
                     "referencias": [reference(s) for s in sources]})
    summary = {"status": "passed", "alcance": "Integridad y procedencia, sin ejecutar casos",
               "fichas_originales_verificadas": len(data), "casos_con_fuentes_verificadas": len(cases),
               "manuales_verificados": len(MANUALS),
               "referencias_comprobadas": sum(len(row["referencias"]) for row in rows),
               "casos_pendientes_de_revision_humana": sum(
                   case["revision_humana"]["estado"] == "pendiente_revision" for case in cases),
               "casos_ejecutados_en_este_ensayo": 0, "catalogos_modificados": False,
               "gobierno_archivado": archived_authority(proposals, cases)}
    return summary, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    summary, rows = audit()
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=False)
        write_json(args.output_dir / "summary.json", summary)
        write_jsonl(args.output_dir, "fuentes", rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
