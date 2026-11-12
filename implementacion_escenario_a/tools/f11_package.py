"""Empaqueta y verifica una copia transportable de la entrega técnica."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from f0_common import write_report
from f11_inventory import EXCLUDED, WEIGHTS, delivery_records
from review_frozen import CONFIRMED, verify as verify_review
from petroandes.extract.output import write_jsonl
from petroandes.index.common import file_digest
from petroandes.paths import APP_ROOT, PROJECT_ROOT, portable, relative_path

ARCHIVE = "PetroAndes_Escenario_A_Entrega_Tecnica_F11.zip"
LEGACY_REPORTS = {"f0", "f1"}
TEXT_EVIDENCE = {".json", ".jsonl", ".log", ".md", ".txt"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def portable_receipt(text):
    text = portable(text)
    for root, label in ((APP_ROOT, "${APP_ROOT}"), (PROJECT_ROOT, "${PROJECT_ROOT}"),
                        (Path.home(), "${USER_HOME}")):
        if root.drive:
            # Algunas trazas guardan repr() dentro de JSON y duplican el escape.
            pattern = r"[\\/]+".join(re.escape(part) for part in re.split(r"[\\/]+", str(root)))
            text = re.sub(pattern, lambda _: label, text, flags=re.IGNORECASE)
    return text


def sources(evidence):
    entries = [row for row in delivery_records() if (row["base"], row["path"]) != ("app", ".mcp.json")]
    for path in sorted(evidence.rglob("*")):
        if path.is_file():
            name = path.relative_to(APP_ROOT).as_posix()
            entries.append({"base": "app", "path": name, "sha256": file_digest(relative_path(name, APP_ROOT))})
    return entries


def read_entry(entry):
    base = {"app": APP_ROOT, "project": PROJECT_ROOT}[entry["base"]]
    path = relative_path(entry["path"], base)
    relative = Path(entry["path"])
    blocked = EXCLUDED | {"artifacts", "models", "node_modules", "reports"}
    if (blocked.intersection(relative.parts) or relative.suffix.lower() in WEIGHTS
            or (relative.name.startswith(".env") and relative.name != ".env.example")):
        raise ValueError(f"Archivo excluido de la entrega: {entry['path']}")
    data = path.read_bytes()
    if sha256(data) != entry["sha256"]:
        raise ValueError(f"El archivo cambió durante el empaquetado: {entry['path']}")
    info = {"sha256": entry["sha256"], "bytes": len(data)}
    if (entry["base"] == "app" and relative.parts[:1] == ("evidence",)
            and len(relative.parts) >= 3 and relative.parts[1] in LEGACY_REPORTS
            and path.suffix in TEXT_EVIDENCE):
        # Los archivos originales conservan sus bytes. El ZIP registra la huella de su propia copia.
        text = data.decode("utf-8-sig")
        redacted = portable_receipt(text)
        if redacted != text:
            data = redacted.encode("utf-8")
            info = {"sha256": sha256(data), "bytes": len(data), "sha256_original": entry["sha256"]}
    name = (Path(APP_ROOT.name) / relative).as_posix() if entry["base"] == "app" else relative.as_posix()
    return name, data, info


def create_archive(destination, evidence, archive_name=ARCHIVE):
    archive = destination / archive_name
    review = verify_review()[0] if (CONFIRMED / "manifest.json").is_file() else None
    manifest_dir = destination / "manifiesto"
    manifest_dir.mkdir()
    entries = sources(evidence)
    records, seen = [], set()
    with ZipFile(archive, "x", compression=ZIP_DEFLATED) as zipped:
        for entry in entries:
            name, data, info = read_entry(entry)
            if name.casefold() in seen or name.split("/", 1)[0].casefold() == "manifiesto":
                raise ValueError(f"Ruta duplicada o reservada en el ZIP: {name}")
            seen.add(name.casefold())
            zipped.writestr(name, data)
            records.append({"path": name, **info})
        filenames = write_jsonl(manifest_dir, "archivos", records)
        manifest = {f"MANIFIESTO/{name}": file_digest(manifest_dir / name) for name in filenames}
        for name in filenames:
            zipped.write(manifest_dir / name, f"MANIFIESTO/{name}")
    expected = {row["path"]: row["sha256"] for row in records} | manifest
    with ZipFile(archive) as zipped:
        if len(zipped.namelist()) != len(expected) or set(zipped.namelist()) != set(expected):
            raise RuntimeError("El índice del ZIP no coincide con su manifiesto")
        for name, digest in expected.items():
            if sha256(zipped.read(name)) != digest:
                raise RuntimeError(f"Huella incorrecta al reabrir el ZIP: {name}")
    digest = file_digest(archive)
    (destination / f"{archive_name}.sha256").write_text(f"{digest}  {archive_name}\n", encoding="ascii")
    return {"status": "passed", "zip": archive_name, "sha256": digest, "bytes": archive.stat().st_size,
            "archivos_verificados": len(expected), "archivos_en_manifiesto": len(records),
            "copias_con_rutas_portables": sum("sha256_original" in row for row in records),
            "evidencia_incluida": evidence.relative_to(APP_ROOT).as_posix(),
            "evaluacion_academica_formal": "pendiente_ejecucion" if review else "pendiente_revision_humana",
            "revision_academica": review}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--archive-name", default=ARCHIVE, help="Nombre del ZIP, sin directorios")
    parser.add_argument("--evidence-dir", required=True,
                        help="Directorio relativo a la app que contiene una corrida F11 aprobada")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.zip", args.archive_name):
        parser.error("Nombre de ZIP inválido")
    evidence = relative_path(args.evidence_dir, APP_ROOT)
    if not evidence.is_relative_to(APP_ROOT / "evidence/f11"):
        parser.error("La evidencia debe estar bajo evidence/f11")
    report = json.loads((evidence / "corrida/summary.json").read_text(encoding="utf-8-sig"))
    if report["status"] != "passed":
        parser.error("La corrida técnica de F11 debe haber pasado")
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    write_report(destination / "summary.json", create_archive(destination, evidence, args.archive_name))


if __name__ == "__main__":
    main()
