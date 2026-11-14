"""Pruebas del grader y cierre seguro; la integración real se ejecuta aparte con Inspector."""
import json
import sys
from contextlib import contextmanager

import pytest

from petroandes.paths import APP_ROOT

sys.path.insert(0, str(APP_ROOT / "tools"))
import f9_mcp_boundaries as boundaries


@pytest.mark.parametrize("result", [
    {}, {"isError": False, "content": [{"text": "parametros_invalidos"}]},
    {"isError": True, "content": []},
    {"isError": True, "content": [{"text": "servicio_no_disponible"}]},
    {"isError": True, "content": [{"text": "parametros_invalidos"}], "structuredContent": {"dato": "canario"}},
])
def test_invalid_input_requires_explicit_schema_rejection(result):
    with pytest.raises(AssertionError):
        boundaries.check_invalid(result)


@pytest.mark.parametrize("changes", [
    {"estado": "error", "error": "indice_no_listo"},
    {"estado": "abstencion"}, {"error": "servicio_no_disponible"},
    {"partes": [{"texto": "canario"}]}, {"citas": [{"doc_id": "oculto"}]},
    {"revision_gobierno": 15},
])
def test_denial_never_accepts_errors_leaks_or_another_snapshot(changes):
    denied = {"estado": "denegado", "error": "evidencia_no_autorizada", "partes": [], "citas": [],
              "revision_gobierno": 13}
    with pytest.raises(AssertionError):
        boundaries.check_denied(denied | changes)


def test_protocol_and_domain_controls_accept_their_distinct_contracts():
    boundaries.check_invalid({"isError": True, "content": [{"text": "parametros_invalidos"}]})
    boundaries.check_denied({"estado": "denegado", "error": "evidencia_no_autorizada", "partes": [],
                              "citas": [], "revision_gobierno": 13})


def test_infrastructure_failure_is_saved_as_failed_not_blocked(tmp_path, monkeypatch):
    @contextmanager
    def broken_fixture(*_):
        raise RuntimeError("Inspector no disponible: control ficticio del manejo de errores")
        yield

    monkeypatch.setattr(boundaries, "configure_cache", lambda **_: None)
    monkeypatch.setattr(boundaries, "historical_lab", broken_fixture)
    destination = tmp_path / "informe"
    summary = boundaries.run(destination)
    recorded = json.loads((destination / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == recorded["status"] == "failed"
    assert summary["llm"] == "no_evaluado" and summary["tipo"] == "RuntimeError"
    assert "comprobaciones" not in summary


def test_evidence_is_not_overwritten(tmp_path):
    with pytest.raises(FileExistsError):
        boundaries.run(tmp_path)
