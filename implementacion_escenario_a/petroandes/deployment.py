"""Configuración local de confianza y conexión de lectura por operación."""
from contextlib import contextmanager
from functools import cached_property

from petroandes.catalog.api import Catalog
from petroandes.catalog.store import index_directory, profile_path
from petroandes.embeddings.cache import configure_cache
from petroandes.embeddings.encoder import E5Encoder
from petroandes.governance.eligibility import EligibilityService
from petroandes.governance.models import ServiceContext
from petroandes.paths import APP_ROOT
from petroandes.retrieve import Retriever


class LocalDeployment:
    def __init__(self, profile):
        self.profile = profile
        self.catalog_path = profile_path(profile)
        self.index = index_directory(profile)

    @cached_property
    def context(self):
        return ServiceContext.model_validate_json(
            (APP_ROOT / "config/f4-context.json").read_text(encoding="utf-8"))

    @cached_property
    def encoder(self):
        configure_cache(offline=True)
        return E5Encoder()

    @contextmanager
    def connect(self):
        with Catalog.open(self.catalog_path, self.profile, read_only=True) as catalog:
            yield Retriever(self.index, EligibilityService(catalog, self.context), self.encoder)
