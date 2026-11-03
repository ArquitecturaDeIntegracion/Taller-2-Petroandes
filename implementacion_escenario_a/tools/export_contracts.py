"""Exporta JSON Schema por definición para conservar cada archivo bajo 200 líneas."""
import argparse
import json
import sys
from pathlib import Path

from project_paths import APP_ROOT as ROOT
sys.path.insert(0, str(ROOT))

from petroandes.contracts.documents import Decision, Document, Fragment, Manifest
from petroandes.contracts.queries import FragmentQuery, SearchQuery
from petroandes.contracts.responses import Citation, FragmentResponse, SearchResponse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    destination = ROOT / args.output_dir
    destination.mkdir(parents=True, exist_ok=False)
    definitions = {}
    for model in (Document, Decision, Fragment, Manifest, Citation, SearchQuery,
                  FragmentQuery, SearchResponse, FragmentResponse):
        schema = model.model_json_schema(ref_template="{model}.json")
        for name, definition in schema.pop("$defs", {}).items():
            if name in definitions and definitions[name] != definition:
                raise ValueError(f"Definición inconsistente: {name}")
            definitions[name] = definition
        definitions[model.__name__] = schema
    for name, definition in sorted(definitions.items()):
        content = json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema",
                              **definition}, indent=2, ensure_ascii=False) + "\n"
        if len(content.splitlines()) > 200:
            raise ValueError(f"Separar definición: {name} supera 200 líneas")
        (destination / f"{name}.json").write_text(content, encoding="utf-8")
    print(f"Exportadas {len(definitions)} definiciones JSON Schema en {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
