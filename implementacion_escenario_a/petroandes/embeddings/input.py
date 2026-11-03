"""Texto completo de embedding y tokenizador offline del bundle fijado."""
import hashlib
import json

from petroandes.paths import APP_ROOT, MODELS_DIR


def bundle_config():
    return json.loads((APP_ROOT / "config/embedding-bundle.json").read_text(encoding="utf-8"))


def passage_input(document, section_title, declared_scope, text, context=""):
    version = document.version_documental or "sin versión"
    return (f"passage: {document.doc_id} | versión {version} | emisión {document.fecha_emision}\n"
            f"{document.titulo}\n{section_title}\nÁmbito declarado: {declared_scope}\n"
            + (context + "\n\n" if context else "") + text)


class E5Tokenizer:
    def __init__(self):
        from transformers import AutoTokenizer

        self.config = bundle_config()
        folder = MODELS_DIR / ("e5-" + self.config["revision"])
        for name, expected in self.config["tokenizer_sha256"].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"Tokenizador distinto del bundle fijado: {name}")
        self.tokenizer = AutoTokenizer.from_pretrained(folder, local_files_only=True,
                                                      trust_remote_code=False)

    def count(self, text):
        return len(self.tokenizer(text, truncation=False, add_special_tokens=True,
                                  verbose=False)["input_ids"])
