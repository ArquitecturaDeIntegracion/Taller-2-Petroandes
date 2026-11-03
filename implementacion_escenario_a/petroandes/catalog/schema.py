"""Migración inicial explícita; las versiones desconocidas no se reparan a ciegas."""
SCHEMA_VERSION = 1
SCHEMA = """
CREATE TABLE metadata (
    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
    schema_version INTEGER NOT NULL,
    perfil TEXT NOT NULL CHECK(perfil IN ('baseline','laboratorio')),
    revision INTEGER NOT NULL CHECK(revision >= 0)
);
CREATE TABLE documents (
    document_key TEXT PRIMARY KEY, pdf_sha256 TEXT NOT NULL, payload TEXT NOT NULL,
    registration_revision INTEGER NOT NULL CHECK(registration_revision >= 1)
);
CREATE TABLE document_history (
    document_key TEXT NOT NULL, pdf_sha256 TEXT NOT NULL, payload TEXT NOT NULL,
    PRIMARY KEY(document_key, pdf_sha256)
);
CREATE TABLE observations (
    observation_id TEXT PRIMARY KEY, document_key TEXT NOT NULL REFERENCES documents,
    pdf_sha256 TEXT NOT NULL, payload TEXT NOT NULL
);
CREATE TABLE relations (relation_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE decisions (
    decision_id TEXT PRIMARY KEY, document_key TEXT NOT NULL REFERENCES documents,
    revision INTEGER UNIQUE NOT NULL, payload TEXT NOT NULL
);
CREATE TABLE conflicts (
    conflict_id TEXT PRIMARY KEY, payload TEXT NOT NULL, resolved_revision INTEGER
);
CREATE TABLE events (
    revision INTEGER PRIMARY KEY CHECK(revision >= 1), event_id TEXT UNIQUE NOT NULL, kind TEXT NOT NULL,
    payload TEXT NOT NULL, recorded_at TEXT NOT NULL,
    pending INTEGER NOT NULL DEFAULT 1 CHECK(pending IN (0,1))
);
PRAGMA user_version = 1;
"""
