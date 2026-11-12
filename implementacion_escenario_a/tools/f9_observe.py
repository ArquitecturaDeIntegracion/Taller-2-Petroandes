"""Observador local del ensayo F9 para las llamadas Python y MCP."""
import json
import os
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from project_paths import APP_ROOT

MARKER = "F9_OBSERVER "
PROCESS = {"subprocess.Popen", "os.system", "os.exec", "os.spawn", "os.posix_spawn", "os.fork",
           "os.forkpty", "os.startfile", "os.startfile/2", "os.kill", "os.killpg"}
NETWORK = {"socket.connect", "socket.bind", "socket.sendto", "socket.sendmsg", "socket.getaddrinfo",
           "socket.gethostbyname", "socket.gethostbyname_ex", "socket.gethostbyaddr", "socket.getnameinfo"}
_events = ContextVar("f9_events", default=None)


def _audit(event, args):
    events = _events.get()
    if events is None:
        return
    if event in PROCESS:
        category = "procesos"
    elif event in NETWORK:
        category = "red"
    elif event in {"open", "sqlite3.connect", "os.listdir", "os.scandir"} and isinstance(args[0], (str, bytes)):
        if "balance" not in Path(os.fsdecode(args[0])).name.casefold():
            return
        category = "balances"
    else:
        return
    events.append({"categoria": category, "evento": event})
    raise PermissionError(f"Efecto bloqueado por el observador F9 ({category})")


sys.addaudithook(_audit)


@contextmanager
def observed():
    events = []
    token = _events.set(events)
    try:
        yield events
    finally:
        _events.reset(token)


def self_check(workspace):
    dummy = workspace / "balance-sintetico.txt"
    dummy.write_text("Dato ficticio para comprobar el observador", encoding="utf-8")
    with observed() as events:
        for probe in (lambda: sys.audit("os.system", b"sonda-f9"),
                      lambda: sys.audit("socket.connect", None, None), dummy.read_bytes):
            try:
                probe()
            except PermissionError:
                continue
            raise RuntimeError("El observador no interceptó su sonda local")
    return events


@contextmanager
def observed_stdio():
    with observed() as events:
        try:
            yield
        finally:
            print(MARKER + json.dumps(events), file=sys.stderr, flush=True)


if __name__ == "__main__":
    sys.path.insert(0, str(APP_ROOT / "tests"))
    from f7_stdio_fixture import main

    main(observe=observed_stdio)
