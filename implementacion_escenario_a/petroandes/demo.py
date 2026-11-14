"""Conexión académica única con snapshot autorizado e índice privado por proceso."""
import json
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory, mkdtemp
from unittest.mock import patch

from petroandes.catalog.api import Catalog
from petroandes.embeddings.cache import configure_cache
from petroandes.embeddings.encoder import E5Encoder
from petroandes.extract import pipeline, staging
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.index import stage
from petroandes.index.common import file_digest
from petroandes.index.publication import Publisher
from petroandes.mcp_server import serve
from petroandes.paths import APP_ROOT, relative_path
from petroandes.retrieve import Retriever

LOGGER = logging.getLogger(__name__)


def configuration():
    data = json.loads((APP_ROOT / "config/mcp-demo.json").read_text(encoding="utf-8"))
    if data["snapshot"]["base"] != "app" or data["perfil"] != "laboratorio":
        raise ValueError("La demostración requiere un snapshot académico de laboratorio")
    source = relative_path(data["snapshot"]["path"], APP_ROOT)
    if file_digest(source) != data["snapshot"]["sha256"]:
        raise ValueError("La huella del snapshot de demostración cambió")
    context = ServiceContext.model_validate(data["contexto"])
    clock = datetime.fromisoformat(data["reloj_historico"])
    if clock.tzinfo is None or clock.utcoffset() is None:
        raise ValueError("El reloj histórico necesita zona horaria")
    return data, source, context, clock


class DemoDeployment:
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.prepared = False

    def prepare(self):
        data, source, context, clock = configuration()
        workspace = Path(mkdtemp(prefix="preparacion-", dir=self.workspace))
        catalog_path = workspace / "catalog.sqlite3"
        copyfile(source, catalog_path)
        if file_digest(catalog_path) != data["snapshot"]["sha256"]:
            raise ValueError("La copia de gobierno no coincide con el snapshot aprobado")
        encoder = E5Encoder()
        with Catalog.open(catalog_path, "laboratorio", read_only=True) as catalog:
            if catalog.verify_revision() != data["revision"]:
                raise ValueError("Revisión de demostración inesperada")
            policy = EligibilityService(catalog, context, clock=lambda: clock)
            if len(policy.eligible().documentos) != 14:
                raise ValueError("La política de demostración no autoriza los catorce documentos previstos")
            # F3 escribe sus derivados exclusivamente en este espacio privado.
            with patch.object(pipeline, "profile_path", lambda _: catalog_path):
                with patch.object(pipeline, "ARTIFACTS_DIR", workspace), \
                        patch.object(staging, "ARTIFACTS_DIR", workspace), \
                        patch.object(stage, "ARTIFACTS_DIR", workspace):
                    ingested = pipeline.ingest("laboratorio", workspace / "f3")
                    prepared = stage.load_stage(workspace / "f3/manifest.json", encoder.tokenizer)
            if ingested["preparados"] != 19 or ingested["fragmentos"] != 92:
                raise ValueError("La ingesta de demostración no conserva el inventario")
            with Publisher(workspace / "index", policy, encoder) as publisher:
                receipt = publisher.publish(prepared)
            if receipt["eligible_documents"] != 14 or receipt["published_fragments"] != 68:
                raise ValueError("La publicación de demostración quedó incompleta")
        self.catalog_path, self.context, self.clock = catalog_path, context, clock
        self.index = workspace / "index"
        self.encoder = encoder
        self.prepared = True
        LOGGER.warning("Demostración académica lista: revisión 15, 14 documentos, 68 fragmentos; reloj %s",
                       clock.isoformat())

    @contextmanager
    def connect(self):
        if not self.prepared:
            self.prepare()
        with Catalog.open(self.catalog_path, "laboratorio", read_only=True) as catalog:
            policy = EligibilityService(catalog, self.context, clock=lambda: self.clock)
            yield Retriever(self.index, policy, self.encoder)


def main():
    configure_cache(offline=True)
    with TemporaryDirectory(prefix="petroandes-demo-") as directory:
        deployment = DemoDeployment(directory)
        serve(deployment.connect)


if __name__ == "__main__":
    main()
