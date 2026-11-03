"""Compara versiones activas por plataforma sin exigir los extras de desarrollo."""
from importlib.metadata import PackageNotFoundError, version
from packaging.requirements import Requirement


def lock_matches(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        requirement = Requirement(line)
        if requirement.marker and not requirement.marker.evaluate():
            continue
        try:
            installed = version(requirement.name)
        except PackageNotFoundError:
            return False
        if installed not in requirement.specifier:
            return False
    return True
