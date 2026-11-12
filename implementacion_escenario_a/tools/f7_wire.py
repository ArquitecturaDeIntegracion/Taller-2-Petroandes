"""Comprueba el canal stdout crudo de un servidor stdio de prueba."""
import argparse
import json
import subprocess
import sys
from queue import Queue
from threading import Thread


def probe(command):
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          text=True, encoding="utf-8") as process:
        lines = Queue()

        def read_lines():
            for line in process.stdout:
                lines.put(line)
            lines.put(None)

        reader = Thread(target=read_lines, daemon=True)
        reader.start()

        def send(message):
            process.stdin.write(json.dumps({"jsonrpc": "2.0", **message}) + "\n")
            process.stdin.flush()

        def receive(request_id):
            line = lines.get(timeout=60)
            assert line is not None, "El servidor cerró stdout sin responder"
            reply = json.loads(line)
            assert reply["jsonrpc"] == "2.0" and reply["id"] == request_id and "error" not in reply
            print(json.dumps(reply, ensure_ascii=True))
            return reply["result"]

        try:
            send({"id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-11-25", "capabilities": {},
                "clientInfo": {"name": "petroandes-sonda-stdio", "version": "1"},
            }})
            session = receive(1)
            assert session["protocolVersion"] == "2025-11-25" and session["serverInfo"]["name"] == "PetroAndes"
            send({"method": "notifications/initialized"})
            send({"id": 2, "method": "tools/call", "params": {"name": "obtener_fragmento", "arguments": {
                "doc_id": "RES-CREG-0043-2024", "version_documental": None, "section_id": "articulo-2",
            }}})
            assert receive(2)["structuredContent"]["estado"] == "encontrado"
            process.stdin.close()
            assert process.wait(timeout=15) == 0 and lines.get(timeout=5) is None
        finally:
            if process.poll() is None:
                process.kill()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command:
        parser.error("Falta el comando del servidor")
    probe(args.command)


if __name__ == "__main__":
    main()
