"""Sirve la copia histórica de F7 por stdio para clientes locales."""
import sys
from contextlib import ExitStack, contextmanager
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import MonkeyPatch

from petroandes.embeddings.cache import configure_cache
from petroandes.mcp_server import serve
from project_paths import APP_ROOT

sys.path.insert(0, str(APP_ROOT / "tests"))
from historical_lab import historical_lab


def main():
    configure_cache(offline=True)
    with TemporaryDirectory(prefix="petroandes-mcp-f7-") as directory, ExitStack() as resources:
        @cache
        def prepare():
            with MonkeyPatch.context() as patch:
                service, _ = resources.enter_context(historical_lab(Path(directory), patch))
            return service

        @contextmanager
        def connect():
            yield prepare()

        # El listado está disponible antes de preparar E5 y el índice.
        # serve dirige los diagnósticos de la primera consulta a stderr.
        serve(connect)


if __name__ == "__main__":
    main()
