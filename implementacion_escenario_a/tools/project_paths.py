"""Bootstrap para ejecutar tools/*.py desde cualquier directorio de trabajo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from petroandes.paths import (APP_ROOT, PROJECT_ROOT, CACHE_DIR, MODELS_DIR,
    INSPECTOR_DIR, model_reference, portable, relative_path, resolve_model_report)
