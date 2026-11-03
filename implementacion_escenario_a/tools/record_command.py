"""Ejecuta argumentos sin shell y conserva salida íntegra en partes de 160 líneas."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from project_paths import APP_ROOT, portable


def record(command, destination, timeout=1800, env=None):
    destination = APP_ROOT / destination
    destination.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    start = perf_counter()
    env = {**(os.environ if env is None else env), "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(command, capture_output=True, encoding="utf-8",
                                errors="replace", timeout=timeout, env=env)
        code, stdout, stderr = result.returncode, portable(result.stdout), portable(result.stderr)
    except subprocess.TimeoutExpired as exc:
        code = 124
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        stdout = stdout.decode("utf-8", "replace") if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode("utf-8", "replace") if isinstance(stderr, bytes) else stderr
        stderr += f"\nTimeout después de {timeout} segundos."
    except OSError as exc:
        code, stdout, stderr = 126, "", f"{type(exc).__name__}: {exc}\n"
    stdout, stderr = portable(stdout), portable(stderr)
    files = []
    for name, content in (("stdout", stdout), ("stderr", stderr)):
        lines = content.splitlines(keepends=True)
        for index in range(0, len(lines), 160):
            path = destination / f"{name}-{index // 160 + 1:03d}.log"
            path.write_text("".join(lines[index:index + 160]), encoding="utf-8")
            files.append(path.name)
    report = {"command": command, "cwd": str(Path.cwd()), "started_utc": started,
              "elapsed_seconds": perf_counter() - start, "exit_code": code,
              "output_files": files}
    (destination / "command.json").write_text(
        json.dumps({"evidence_schema_version": 2, "path_encoding": "portable-placeholders",
                    **portable(report)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report, stdout, stderr


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("Falta el comando")
    report, stdout, stderr = record(command, args.destination)
    print(stdout, end="")
    print(stderr, end="", file=sys.stderr)
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
