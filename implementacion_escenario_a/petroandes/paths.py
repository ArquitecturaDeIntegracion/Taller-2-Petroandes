"""Raíces y referencias portables; las rutas se resuelven al ejecutar, no al registrar."""
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

APP_ROOT = Path(__file__).resolve().parents[1]


def configured(name, default, base=APP_ROOT):
    value = Path(os.environ.get(name, str(default))).expanduser()
    return (value if value.is_absolute() else base / value).resolve()


PROJECT_ROOT = configured("PETROANDES_PROJECT_ROOT", APP_ROOT.parent)
CACHE_DIR = configured("PETROANDES_CACHE_DIR", ".cache")
MODELS_DIR = configured("PETROANDES_MODELS_DIR", CACHE_DIR / "models")
ARTIFACTS_DIR = configured("PETROANDES_ARTIFACTS_DIR", "artifacts")
INSPECTOR_DIR = configured("PETROANDES_INSPECTOR_DIR", CACHE_DIR / "inspector")
if ("PETROANDES_INSPECTOR_DIR" not in os.environ and not INSPECTOR_DIR.exists()
        and (APP_ROOT / ".venv/inspector").is_dir()):
    INSPECTOR_DIR = APP_ROOT / ".venv/inspector"  # transición del entorno F0 existente


def relative_path(value, base):
    """Lee referencias nuevas POSIX y relativas Windows históricas, sin escapes."""
    text = str(value)
    if PureWindowsPath(text).is_absolute() or PurePosixPath(text).is_absolute():
        raise ValueError("Se esperaba una referencia relativa, no una ruta absoluta")
    parts = text.replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError("La referencia no puede salir de su raíz")
    result = (Path(base) / Path(*parts)).resolve()
    if not result.is_relative_to(Path(base).resolve()):
        raise ValueError("Referencia fuera de la raíz autorizada")
    return result


def model_reference(path):
    return {"base": "models", "path": Path(path).resolve().relative_to(MODELS_DIR).as_posix()}


def resolve_model_report(report, family):
    ref = report.get("snapshot_ref")
    if ref:
        if ref.get("base") != "models":
            raise ValueError("Base de modelo desconocida")
        return relative_path(ref["path"], MODELS_DIR)
    # Migración de lectura: no reutilizar snapshot absoluto de evidencias históricas.
    revision = report.get("revision", "")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("La evidencia histórica no identifica una revisión válida")
    return relative_path(f"{family}-{revision}", MODELS_DIR)


def portable(value):
    """Redacta ubicaciones del entorno en NUEVAS evidencias; no toca las anteriores."""
    if isinstance(value, dict):
        return {str(k).replace("\\", "/"): portable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [portable(item) for item in value]
    if not isinstance(value, (str, Path)):
        return value
    text = str(value)
    if text == sys.executable:
        return "python"
    roots = [(MODELS_DIR, "${MODELS_DIR}"), (INSPECTOR_DIR, "${INSPECTOR_DIR}"),
             (APP_ROOT, "${APP_ROOT}"), (PROJECT_ROOT, "${PROJECT_ROOT}"),
             (Path.home(), "${USER_HOME}"), (Path(tempfile.gettempdir()), "${TMPDIR}")]
    for root, label in roots:
        for variant in {str(root), root.as_posix(), str(root).replace("\\", "\\\\")}:
            text = re.sub(re.escape(variant), lambda _: label, text,
                          flags=re.IGNORECASE if os.name == "nt" else 0)
    return text
