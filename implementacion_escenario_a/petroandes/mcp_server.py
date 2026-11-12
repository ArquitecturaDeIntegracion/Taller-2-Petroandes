"""Punto de entrada stdio para el servidor documental de PetroAndes."""
import argparse
import os
import sys
from contextlib import contextmanager


@contextmanager
def protocol_stdout():
    sys.stdout.flush()
    fd = sys.stdout.fileno()
    with os.fdopen(os.dup(fd), "w", encoding="utf-8", newline="\n") as protocol:
        # El SDK conserva el duplicado. Los prints y las escrituras nativas a
        # stdout del resto del proceso llegan a stderr.
        os.dup2(sys.stderr.fileno(), fd)
        try:
            yield protocol
        finally:
            try:
                sys.stdout.flush()
            finally:
                os.dup2(protocol.fileno(), fd)


def serve(connect):
    with protocol_stdout() as output:
        import anyio
        from mcp.server.stdio import stdio_server
        from petroandes.mcp_tools import create_server

        async def run():
            server = create_server(connect)
            async with stdio_server(stdout=anyio.wrap_file(output)) as (reader, writer):
                await server.run(reader, writer, server.create_initialization_options())

        anyio.run(run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=("baseline", "laboratorio"))
    profile = parser.parse_args().profile

    def connect():
        from petroandes.deployment import LocalDeployment

        nonlocal deployment
        if deployment is None:
            deployment = LocalDeployment(profile)
        return deployment.connect()

    deployment = None
    serve(connect)


if __name__ == "__main__":
    main()
