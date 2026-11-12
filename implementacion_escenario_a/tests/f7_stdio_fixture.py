"""Proceso stdio para el ensayo histórico aislado de F7."""
import argparse
import json
import os
from contextlib import contextmanager, nullcontext
from datetime import datetime
from functools import cache
from pathlib import Path

from petroandes.mcp_server import serve


def main(observe=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    data = json.loads(parser.parse_args().fixture.read_text(encoding="utf-8"))

    @cache
    def encoder():
        from petroandes.embeddings.cache import configure_cache
        from petroandes.embeddings.encoder import E5Encoder

        configure_cache(offline=True)
        print(f"F7 fixture stdout Python pid={os.getpid()}", flush=True)
        os.write(1, b"F7 fixture stdout nativo\n")
        return E5Encoder()

    @contextmanager
    def connect():
        from petroandes.catalog.api import Catalog
        from petroandes.governance.eligibility import EligibilityService
        from petroandes.governance.models import ServiceContext
        from petroandes.retrieve import Retriever

        at = datetime.fromisoformat(data["at"])
        context = ServiceContext.model_validate(data["context"])
        with Catalog.open(data["catalog"], "laboratorio", read_only=True) as catalog:
            model = encoder()
            with observe() if observe else nullcontext():
                yield Retriever(Path(data["index"]), EligibilityService(catalog, context, clock=lambda: at), model)

    serve(connect)


if __name__ == "__main__":
    main()
