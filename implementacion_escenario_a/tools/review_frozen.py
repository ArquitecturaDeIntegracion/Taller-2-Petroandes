"""Valida el manifiesto congelado, las fuentes y los contratos sin ejecutar casos."""
import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from review_case_sources import reference
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.extract.output import write_json
from petroandes.governance.models import ServiceContext
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT, relative_path

CONFIRMED = APP_ROOT / "docs/revision/20261108-confirmada"
EVIDENCE = APP_ROOT / "evidence/revision/20261108-confirmada"
CHANGED = frozenset({"A02", "A03", "A07", "R09", "R10", "R13", "R16"})
QUERIES = {"buscar_documentos": SearchQuery, "obtener_fragmento": FragmentQuery}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_hashes(root, hashes):
    for name, expected in hashes.items():
        require(file_digest(relative_path(name, root)) == expected, f"Huella inválida: {name}")


def context_for(case, usage=None):
    context = case["contexto_servicio_solo_fixture"]
    return ServiceContext(identidad=context["identidad"], grupos=frozenset(context["grupos"]),
                          ambito=context["ambito"], uso=usage or context["uso"])


def clock_for(case):
    clock = datetime.fromisoformat(case["contexto_servicio_solo_fixture"]["fecha_solo_para_reloj_de_pruebas"])
    require(clock.utcoffset() is not None, f"Falta zona del reloj: {case['case_id']}")
    return clock


def check_review(item, original, name, human):
    require(all(item["revision_humana"].get(key) == value for key, value in human.items()),
            f"Revisión humana incompleta: {name}")
    require(bool(item["revision_humana"]["justificacion"]), f"Falta justificación: {name}")
    require(item["ficha_original"] == {"path": f"../{name}",
                                      "sha256": original["sha256_fichas_propuestas"][name]},
            f"Referencia original incorrecta: {name}")


def verify():
    manifest_path = CONFIRMED / "manifest.json"
    manifest = load(manifest_path)
    original_path = CONFIRMED.parent / "manifest.json"
    original = load(original_path)
    require(manifest["sha256_manifiesto_original"] == file_digest(original_path), "Cambió el manifiesto original")
    check_hashes(CONFIRMED.parent, original["sha256_fichas_propuestas"])
    check_hashes(CONFIRMED, manifest["sha256_archivos"])
    check_hashes(APP_ROOT, manifest["sha256_configuracion"])
    cases = []
    references = 0
    human = manifest["revision_humana"]
    require(human["estado"] == "aprobada" and human["revisor"] and human["fecha"],
            "Revisión humana sin autor o fecha")
    require(manifest["case_refs"] == original["case_refs"], "Se alteró la identidad de la partición")
    require(manifest["decision_refs"] == [f"decisiones/{key}.json" for key in ("D01", "D02", "D03")],
            "Las fichas documentales no coinciden con lo confirmado")
    files = manifest["case_refs"] + manifest["decision_refs"] + ["autorizacion.md", "matriz.md", "protocolo.json"]
    require(len(files) == len(set(files)) and set(files) == set(manifest["sha256_archivos"]),
            "El inventario congelado contiene faltantes, duplicados o referencias sin hash")
    for name in manifest["case_refs"]:
        case = load(relative_path(name, CONFIRMED))
        previous = load(relative_path(name, CONFIRMED.parent))
        check_review(case, original, name, human)
        key = case["case_id"]
        require(case["particion"] == previous["particion_propuesta"] and key == previous["case_id"],
                f"Identidad o partición modificadas: {name}")
        require(case["congelado_para_evaluacion"] and case["estado_ejecucion"] == "no_ejecutado"
                and case["metricas"] is None, f"Estado académico incoherente: {key}")
        expected = "aprobar_con_correcciones" if key in CHANGED else "aprobar_sin_cambio_de_fondo"
        require(case["revision_humana"]["decision_humana"] == expected, f"Decisión incorrecta: {key}")
        oracle = case["oracle"]
        if key not in CHANGED:
            require(oracle == previous["oracle_propuesto"] and case["pregunta"] == previous["pregunta"],
                    f"Cambio de fondo en caso aprobado sin cambios: {key}")
        require(case["precondiciones"]["propuestas_documentales_requeridas"]
                == previous["precondiciones"]["propuestas_documentales_requeridas"], f"Cambio de permisos: {key}")
        refs = oracle["evidencia_a_recuperar_y_citar"] + oracle["fuentes_para_revision_humana"]
        references += len(refs)
        for source in refs:
            reference(source)
        clock_for(case)
        for call in case["llamadas_principales"]:
            QUERIES[call["herramienta"]].model_validate(call["argumentos"])
            context_for(case, call["uso"])
        cases.append(case)
    counts = Counter(case["particion"] for case in cases)
    require(counts == {"ajuste": 8, "reserva": 16}, "Partición congelada inválida")
    security = next(case for case in cases if case["case_id"] == "R16")
    require([(row["herramienta"], row["uso"]) for row in security["llamadas_principales"]]
            == [("obtener_fragmento", "inspeccion_no_confiable"), ("buscar_documentos", "evidencia_historica")]
            and security["oracle"]["acceso_directo_esperado"]["estado"] == "encontrado"
            and security["oracle"]["busqueda_esperada"]["estado"] == "abstencion"
            and not security["oracle"]["recall_aplicable"], "R16 debe conservar ambos controles")
    for name in manifest["decision_refs"]:
        item = load(relative_path(name, CONFIRMED))
        check_review(item, original, name, human)
        for source in [item["documento"]["pdf"], *item["evidencia_corpus"]["fuentes"]]:
            reference(source)
            references += 1
    summary = {"status": "passed", "alcance": "Integridad, fuentes, partición y contratos",
               "manifiesto_sha256": file_digest(manifest_path), "casos_congelados": dict(counts),
               "correcciones_aprobadas": sorted(CHANGED), "referencias_pdf_verificadas": references,
               "fichas_originales_verificadas": len(original["sha256_fichas_propuestas"]),
               "decisiones_documentales": len(manifest["decision_refs"]), "casos_ejecutados": 0}
    return summary, cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    summary, _ = verify()
    path = parser.parse_args().output
    if path:
        write_json(path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
