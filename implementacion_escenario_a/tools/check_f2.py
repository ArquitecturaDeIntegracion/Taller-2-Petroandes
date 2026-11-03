"""Verifica catálogos iniciales persistentes desde otro proceso; no aprueba el laboratorio."""
import argparse
import hashlib
import json

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path
from petroandes.contracts.common import Scope
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.paths import APP_ROOT, PROJECT_ROOT, relative_path
from f0_common import write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    evidence = APP_ROOT / args.evidence_dir
    results = []
    context = ServiceContext(identidad="sonda-tecnica-sin-autorizacion",
        grupos=frozenset(["sin-permisos"]), ambito=Scope(tipo="general", identificador="corpus"),
        uso="evidencia_historica")
    for perfil in ("baseline", "laboratorio"):
        with Catalog.open(profile_path(perfil), perfil) as catalog:
            snapshot = catalog.snapshot()
            result = catalog.summary()
            assert result["clasificacion"] == {"pendiente": 15, "excluido": 4, "certificado": 0}
            assert result["documentos"] == 19 and result["decisiones_registradas"] == 0
            assert result["governance_revision"] == result["eventos_pendientes"] == 1
            policy = EligibilityService(catalog, context)
            assert policy.eligible().documentos == ()
            assert all(policy.authorize(doc).documentos == () for doc in snapshot.documentos)
            for doc in snapshot.documentos:
                if not doc.pdf_uri.startswith("project:"):
                    raise ValueError("Referencia PDF sin base explícita")
                pdf = relative_path(doc.pdf_uri.removeprefix("project:"), PROJECT_ROOT)
                assert hashlib.sha256(pdf.read_bytes()).hexdigest() == doc.pdf_sha256
            archive = evidence / perfil
            saved = json.loads((archive / "summary.json").read_text(encoding="utf-8"))
            assert hashlib.sha256((archive / "catalog.sqlite3").read_bytes()).hexdigest() == saved["backup_sha256"]
            with Catalog.open(archive / "catalog.sqlite3", perfil, read_only=True) as copy:
                assert copy.summary() == result
            results.append({**result, "elegibles": 0, "accesos_directos_denegados": 19,
                            "hashes_pdf_conservados": 19, "backup_verificado": True})
    write_report(APP_ROOT / args.output, {"status": "passed", "profiles": results,
        "technical_F2_initialization_verified": True, "academic_review_pending": True,
        "certificaciones_humanas_creadas": 0, "phase_F2_complete": False,
        "scope": "Catálogo y política F2; no acredita índices, recuperación ni herramientas F7"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
