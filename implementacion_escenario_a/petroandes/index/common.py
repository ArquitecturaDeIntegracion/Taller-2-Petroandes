"""Huellas lógicas y claves de publicación reproducibles."""
import hashlib
import json
from uuid import NAMESPACE_URL, uuid5


class IndexUnavailable(RuntimeError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_digest(path):
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def generation_id(value):
    return str(uuid5(NAMESPACE_URL, digest(value)))


def context_data(context):
    data = context.model_dump(mode="json")
    data["grupos"] = sorted(data["grupos"])
    return data
