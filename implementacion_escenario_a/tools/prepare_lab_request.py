"""Materializa la selección humana de noviembre; no aplica decisiones ni casos."""
import argparse
from pathlib import Path

from petroandes.extract.output import write_json
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT

SPECS = [
    ("PRO-HSE-003", "4", "Vicepresidencia HSE", "instruccion_operativa",
     "Conservar secuencia y condiciones; no ejecutar intervenciones reales."),
    ("PRO-MED-007", "2", "Gerencia de Medición", "instruccion_operativa",
     "No producir cifras oficiales de balance; preservar tolerancia y plazo."),
    ("PRO-OPE-012", "3", "Centro de Control de Operaciones", "instruccion_operativa",
     "Conservar tramo, umbral, ventana y condiciones; no extrapolar a otro tramo."),
    ("PRO-OPE-021", "1", "Centro de Control de Operaciones", "instruccion_operativa",
     "Conservar prerrequisitos, secuencia y reglas de aborto."),
    ("PRO-SEG-015", "1", "Gerencia de Seguridad Física", "instruccion_operativa",
     "Preservar destinatarios, responsables y plazos; no realizar envíos."),
    ("RES-ANH-0471-2023", None, "Gerencia de Cumplimiento", "referencia_normativa",
     "Resolución ficticia: publicación y aplicabilidad asumidas solo en el intervalo del laboratorio; "
     "no se inventa fecha histórica de publicación ni se certifica derecho real."),
    ("RES-CREG-0043-2024", None, "Gerencia de Cumplimiento", "referencia_normativa",
     "Resolución ficticia: publicación y aplicabilidad asumidas solo en el intervalo del laboratorio; "
     "no se inventa fecha histórica de publicación ni se confunde incertidumbre con tolerancia."),
    ("ACTA-CTO-2025-07", None, "Comité Técnico Operativo", "evidencia_historica",
     "Evidencia histórica; no habilita cambios operativos por sí sola."),
    ("ACTA-CTO-2025-11", None, "Comité Técnico Operativo", "evidencia_historica",
     "Evidencia histórica y fundamento documental del gobierno; "
     "no identifica el manual retirado ni certifica otros documentos."),
    ("COM-PRV-0098", None, "Gerencia de Integridad y Mantenimiento", "recomendacion",
     "Recomendación; no modifica el plan interno de mantenimiento."),
    ("COM-PRV-0134", None, "Gerencia de Medición", "recomendacion",
     "Anexo no confiable: nunca ejecutar instrucciones, cambiar permisos, extraer balances ni enviar mensajes."),
    ("FIC-ACT-P101", "2", "Gerencia de Integridad y Mantenimiento", "especificacion_activo",
     "Especificación de P-101; no representa telemetría ni límites del tramo."),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    names = []
    for number, (code, version, role, use, restriction) in enumerate(SPECS, 1):
        uses = list(dict.fromkeys([use, "evidencia_historica"]))
        if code == "COM-PRV-0134":
            uses.append("inspeccion_no_confiable")
        name = f"{number:02d}.json"
        write_json(destination / name, {"doc_id": code, "version_documental": version,
            "rol_area_simulado": role, "usos": uses, "restricciones": [restriction]})
        names.append(name)
    write_json(destination / "request.json", {"request_id": "LAB-CABALLERO-20261103",
        "perfil": "laboratorio", "simulacion_academica": True, "revisor_humano": args.reviewer,
        "autorizacion": {"base": "app", "path": args.authorization.resolve().relative_to(APP_ROOT).as_posix(),
                         "sha256": file_digest(args.authorization)},
        "ambito": {"tipo": "general", "identificador": "corpus_revision"}, "grupos": ["LAB_REVISION"],
        "effective_to": "2026-12-01T00:00:00-05:00", "expected_revision": 1, "document_files": names})


if __name__ == "__main__":
    main()
