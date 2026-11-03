"""CLI F3: preparar desde PDF en staging, sin activar índices ni otorgar permisos."""
import argparse
import json

from .pipeline import ingest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["baseline", "laboratorio"], default="baseline")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    result = ingest(args.profile, args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["rechazados"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
