"""Interfaz interna pequeña sobre almacenamiento, historial y política de gobierno."""
from . import decisions, documents, snapshot
from .store import Store


class Catalog(Store):
    def seed(self, corpus, observations, relations):
        return documents.seed(self, corpus, observations, relations)

    def put_document(self, document, expected_revision):
        return documents.put_document(self, document, expected_revision)

    def apply_decision(self, record, expected_revision):
        return decisions.apply_decision(self, record, expected_revision)

    def add_conflict(self, conflict, expected_revision):
        return decisions.add_conflict(self, conflict, expected_revision)

    def resolve_conflict(self, conflict_id, reviewer, expected_revision):
        return decisions.resolve_conflict(self, conflict_id, reviewer, expected_revision)

    def snapshot(self):
        return snapshot.read_snapshot(self)

    def summary(self):
        return snapshot.summary(self)
