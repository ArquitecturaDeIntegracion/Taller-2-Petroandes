"""Servidor mínimo de compatibilidad F0; no expone todavía el corpus."""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PetroAndes-F0")


@mcp.tool()
def comprobar_entorno() -> dict[str, str]:
    """Comprueba el transporte de laboratorio; no concede permisos ni vigencia."""
    return {"estado": "ok", "fase": "F0", "origen": "prueba_sintetica"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
