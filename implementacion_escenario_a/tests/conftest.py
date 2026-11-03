"""Prepara únicamente el padre del directorio temporal solicitado a pytest."""
from pathlib import Path


def pytest_configure(config):
    if config.option.basetemp:
        Path(config.option.basetemp).resolve().parent.mkdir(parents=True, exist_ok=True)
