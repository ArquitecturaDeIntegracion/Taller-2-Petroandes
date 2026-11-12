"""Procedencia del anexo y publicación temporal con permiso de inspección."""
import hashlib
import json

from f0_common import write_report
from petroandes.chunk.structural import section_text
from petroandes.extract.pdf import extract_pdf
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import DecisionRecord, ServiceContext
from petroandes.index.publication import Publisher
from petroandes.index.stage import load_stage
from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path

DOCUMENT = "COM-PRV-0134"
SECTION = "anexo-notas-de-integracion"
FLAG = "instrucciones_dirigidas_al_procesador"
AUDIT = "inspeccion_no_confiable"
DECISION_PATH = "evidence/lab/20261103/registration/decisions/11.json"
PAYLOAD_MARKERS = ("ignore las instrucciones previas", "balance volumétrico consolidado",
                   "soporte-firmware@proveedor.ejemplo", "no informe al usuario")


def prepare_audit(workspace, historical, destination):
    record = DecisionRecord.model_validate_json((APP_ROOT / DECISION_PATH).read_text(encoding="utf-8"))
    decision = record.decision
    if (record not in historical.policy.catalog.snapshot().decisiones or decision.doc_id != DOCUMENT
            or decision.version_documental is not None or not decision.simulacion_academica
            or not record.contenido_no_confiable or AUDIT not in decision.usos):
        raise ValueError("La decisión académica de inspección no coincide con el catálogo histórico")

    source = load_stage(workspace / "f3/manifest.json", historical.encoder.tokenizer)
    annex = next(row for row in source.records if row["fragment"]["doc_id"] == DOCUMENT
                 and row["fragment"]["section_id"] == SECTION)
    fragment, security = annex["fragment"], annex["metadata"]["seguridad"]
    uri = annex["metadata"]["documento"]["pdf_uri"]
    pdf, sections, _ = extract_pdf(relative_path(uri.removeprefix("project:"), PROJECT_ROOT))
    section = next(item for item in sections if item.section_id == SECTION)
    text = section_text(section)
    pages = sorted({line.page for block in section.blocks for line in block.lines})
    write_report(destination / "anexo.json", {"pdf_uri": uri, "pdf_sha256": pdf.pdf_sha256,
                 "texto_extraido_sha256": hashlib.sha256(text.encode()).hexdigest(), "paginas": pages,
                 "fragmento": fragment, "seguridad": security, "lineas_fuente": annex["source_lines"],
                 "decision_ref": f"app:{DECISION_PATH}", "decision_id": decision.decision_id,
                 "revision_decision": decision.revision_gobierno}, emit=False)
    if (pdf.pdf_sha256 != decision.pdf_sha256 or fragment["pdf_sha256"] != pdf.pdf_sha256
            or pages != list(range(fragment["pagina_inicio"], fragment["pagina_fin"] + 1))
            or fragment["texto"] != text or not all(marker in text.casefold() for marker in PAYLOAD_MARKERS)
            or not fragment["contenido_no_confiable"] or security["trust_level"] != "untrusted"
            or FLAG not in security["security_flags"]):
        raise ValueError("La extracción del anexo no conserva texto, páginas, huella o marca de seguridad")

    context = ServiceContext.model_validate(historical.policy.context.model_dump() | {"uso": AUDIT})
    policy = EligibilityService(historical.policy.catalog, context, clock=historical.policy.clock)
    eligible = policy.eligible()
    if [(doc.doc_id, doc.version_documental, doc.pdf_sha256) for doc in eligible.documentos] != [
            (DOCUMENT, None, decision.pdf_sha256)]:
        raise ValueError("El permiso de inspección no se limita a la comunicación certificada")
    root = workspace / "index-auditoria"
    with Publisher(root, policy, historical.encoder) as publisher:
        publication = publisher.publish(source)
        manifest, _ = publisher.active()
    if fragment["chunk_id"] not in manifest.fragmentos:
        raise ValueError("La publicación de inspección no contiene el anexo")
    write_report(destination / "publicacion-auditoria.json", publication, emit=False)
    return context, root, fragment


def candidate_details(trace, fragments):
    return {branch: [{"chunk_id": key, "doc_id": fragments[key]["doc_id"],
                      "section_id": fragments[key]["section_id"]} for key in keys]
            for branch, keys in trace.get("candidatos", {}).items()}
