"""Verifica debugpy por DAP con un breakpoint real, sin automatizar VS Code."""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
from project_paths import APP_ROOT
from f0_common import write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    source = APP_ROOT / "tools/preflight.py"
    line = next(i for i, text in enumerate(source.read_text().splitlines(), 1)
                if 'registry = json.loads' in text)
    process = subprocess.Popen([sys.executable, "-B", "-m", "debugpy", "--listen",
        f"127.0.0.1:{port}", "--wait-for-client", str(source)], cwd=APP_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    connection = None
    seq = 0
    stopped = verified = False
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                connection = socket.create_connection(("127.0.0.1", port), timeout=1)
                break
            except (ConnectionRefusedError, TimeoutError):
                if process.poll() is not None:
                    raise RuntimeError(process.communicate()[1])
                time.sleep(0.1)
        if connection is None:
            raise TimeoutError("El adaptador debug no inició")
        connection.settimeout(30)
        reader = connection.makefile("rb")

        def send(command, arguments):
            nonlocal seq
            seq += 1
            payload = json.dumps({"seq": seq, "type": "request", "command": command,
                                  "arguments": arguments}).encode()
            connection.sendall(f"Content-Length: {len(payload)}\r\n\r\n".encode() + payload)

        def receive():
            headers = {}
            while True:
                raw = reader.readline()
                if not raw:
                    raise EOFError("El adaptador cerró la conexión")
                if raw == b"\r\n":
                    break
                key, value = raw.decode().split(":", 1)
                headers[key.lower()] = value.strip()
            return json.loads(reader.read(int(headers["content-length"])))

        send("initialize", {"adapterID": "python", "clientID": "portable-smoke",
                            "linesStartAt1": True, "pathFormat": "path"})
        while True:
            message = receive()
            if message.get("command") == "initialize":
                assert message["success"], message
                break
        send("attach", {"justMyCode": True})
        while receive().get("event") != "initialized":
            pass
        send("setBreakpoints", {"source": {"path": str(source)},
                                "breakpoints": [{"line": line}]})
        send("configurationDone", {})
        for _ in range(100):
            message = receive()
            if message.get("command") == "setBreakpoints":
                verified = message["body"]["breakpoints"][0]["verified"]
            if message.get("event") == "stopped":
                stopped = message["body"]["reason"] == "breakpoint"
                send("continue", {"threadId": message["body"]["threadId"]})
            if message.get("event") == "terminated":
                send("disconnect", {"terminateDebuggee": False})
                break
        reader.close()
        connection.close()
        connection = None
        stdout, stderr = process.communicate(timeout=15)
        assert process.returncode == 0, stderr
        assert verified and stopped
        assert not json.loads(stdout)["phase_F0_complete"]
        write_report(APP_ROOT / args.output, {"status": "passed",
            "debug_adapter": "debugpy", "protocol": "DAP", "bind": "loopback",
            "breakpoint_verified": verified, "breakpoint_hit": stopped,
            "client_disconnect_sent": True,
            "debuggee_exit_code": process.returncode,
            "scope": "Adaptador y ejecución reales; no automatiza la interfaz de VS Code"})
        return 0
    finally:
        if connection:
            connection.close()
        if process.poll() is None:
            process.terminate()
            process.communicate(timeout=15)


if __name__ == "__main__":
    raise SystemExit(main())
