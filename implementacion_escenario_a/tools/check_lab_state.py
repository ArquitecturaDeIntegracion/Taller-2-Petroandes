"""Evidencia histórica y actual del laboratorio; no aprueba casos ni escribe gobierno."""
import argparse
import json
from datetime import timedelta
from pathlib import Path

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import profile_path, index_directory
from petroandes.extract.output import write_json
from petroandes.governance.administration import load_request
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT


def baseline_identity():
    with Catalog.open(profile_path("baseline"), "baseline", read_only=True) as catalog:
        summary = catalog.summary()
    root = index_directory("baseline")
    return {"catalog_sha256": file_digest(profile_path("baseline")), "summary": summary,
            "index_files_sha256": {p.relative_to(root).as_posix(): file_digest(p)
                                   for p in sorted(root.rglob("*")) if p.is_file()},
            "service_context_sha256": file_digest(APP_ROOT / "config/f4-context.json"),
            "case_files_sha256": {p.relative_to(APP_ROOT).as_posix(): file_digest(p)
                                  for p in sorted((APP_ROOT / "docs/revision/casos").glob("*.json"))}}


def check_current(request, initial, registration):
    identity = baseline_identity()
    assert identity == initial
    results = {}
    with Catalog.open(profile_path("laboratorio"), "laboratorio", read_only=True) as store:
        summary = store.summary()
        assert summary["clasificacion"] == {"certificado": 12, "pendiente": 3, "excluido": 4}
        assert summary["governance_revision"] == summary["eventos_pendientes"] == 13
        assert summary["decisiones_registradas"] == 12
        snapshot = store.snapshot()
        records = snapshot.decisiones
        assert len({r.decision.revisado_en for r in records}) == 1
        reviewed = records[0].decision.revisado_en
        assert reviewed.isoformat() == registration["reviewed_at"]
        for record in records:
            d = record.decision
            assert d.perfil == "laboratorio" and d.simulacion_academica
            assert d.revisor_humano == request.revisor_humano
            assert d.effective_from == d.revisado_en == reviewed
            assert d.effective_to == request.effective_to and not d.intervalo_abierto_expreso
            assert d.autoridad.startswith("SIMULACIÓN ACADÉMICA:") and record.supuesto
            document = next(doc for doc in snapshot.documentos if doc.doc_id == d.doc_id
                            and doc.version_documental == d.version_documental)
            assert document.pdf_sha256 == d.pdf_sha256
        events = store.db.execute("SELECT revision,recorded_at FROM events WHERE revision>1 ORDER BY revision").fetchall()
        assert [r[0] for r in events] == list(range(2, 14))
        from datetime import datetime
        assert all(datetime.fromisoformat(time) >= reviewed for _, time in events)
        for usage, expected in (("evidencia_historica", 12), ("instruccion_operativa", 5),
                ("referencia_normativa", 2), ("recomendacion", 2), ("inspeccion_no_confiable", 1),
                ("especificacion_activo", 1), ("limite_diseno", 0)):
            context = ServiceContext(identidad="sonda-administrativa-local", grupos=frozenset(request.grupos),
                                     ambito=request.ambito, uso=usage)
            policy = EligibilityService(store, context)
            result = policy.eligible()
            assert len(result.documentos) == expected
            results[usage] = [doc.doc_id for doc in result.documentos]
            assert EligibilityService(store, context, clock=lambda: request.effective_to).eligible().documentos == ()
            assert EligibilityService(store, context, clock=lambda: reviewed - timedelta(microseconds=1)
                                      ).eligible().documentos == ()
            if usage == "evidencia_historica":
                assert not any(doc.tipo == "manual" for doc in result.documentos)
                assert EligibilityService(store, context.model_copy(update={"grupos": frozenset(["OTRO"])})
                                          ).eligible().documentos == ()
        service = ServiceContext.model_validate_json((APP_ROOT / "config/f4-context.json").read_text())
        assert EligibilityService(store, service).eligible().documentos == ()
        # Volver a comprobar los snapshots históricos sin cambiar sus verificaciones.
        historical = []
        for profile in ("baseline", "laboratorio"):
            path = APP_ROOT / f"evidence/f2/initial-20261101/{profile}/catalog.sqlite3"
            with Catalog.open(path, profile, read_only=True) as old:
                assert old.summary()["clasificacion"] == {"pendiente": 15, "excluido": 4, "certificado": 0}
                historical.append({"perfil": profile, "sha256": file_digest(path), "revision": old.verify_revision()})
    return {"status": "passed", "laboratorio": summary, "eligible_by_use": results,
        "reviewed_at": reviewed.isoformat(), "historical_snapshots": historical,
        "baseline_byte_identical": True, "service_context_unchanged": True,
        "case_files_unchanged": True, "service_eligible_documents": 0,
        "period_boundaries_denied": True, "cases_approved": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("before", "after"))
    parser.add_argument("--initial", type=Path)
    parser.add_argument("--registration", type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "before":
        report = baseline_identity()
    else:
        report = check_current(load_request(args.request), json.loads(args.initial.read_text()),
                               json.loads(args.registration.read_text()))
    write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
