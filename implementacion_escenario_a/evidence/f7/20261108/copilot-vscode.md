# Pruebas de PetroAndes con Copilot en VS Code

Fecha 2026-11-08, America/Bogota. VS Code 1.145.2 en Windows, destino Local,
Docker Compose con perfil `dev`. [Guía de la práctica](../../../docs/copilot-vscode.md).

VS Code detectó las dos entradas de `.vscode/mcp.json` y los cuatro archivos
de `.github/prompts/`. La comprobación de stdio ejecutó los comandos de la
configuración desde la carpeta de implementación.

```powershell
docker compose --profile dev run --rm --no-deps -T dev -m petroandes.mcp_server --profile laboratorio
docker compose --profile dev run --rm --no-deps -T dev tools/f7_historical_mcp.py
```

Ambos procesos negociaron MCP y listaron `buscar_documentos` y
`obtener_fragmento`. Los argumentos de los prompts devolvieron la revisión 13
y los resultados de la tabla. El cliente de prueba comprobó stdout JSON-RPC
y el cierre limpio de ambos procesos. La primera consulta histórica tardó
71,96 segundos y la siguiente 0,89 segundos en la sonda stdio.

| Prompt ejecutado en Copilot | Herramienta y servidor observados | Resultado |
| --- | --- | --- |
| `/petroandes-01` | `buscar_documentos` en `petroandes-local` | `abstencion` y `sin_evidencia_autorizada`. |
| `/petroandes-02` | `obtener_fragmento` en `petroandes-local` | `denegado` y `evidencia_no_autorizada`. |
| `/petroandes-03` | `buscar_documentos` en `petroandes-historico-f7` | `respondida`, 1.180 psi de diseño y 1.240 psi de alarma, ficha P-101 v2, sección 2, página 1. |
| `/petroandes-04` | `buscar_documentos` en `petroandes-historico-f7` | `respondida`, 0,3 %, resolución RES-CREG-0043-2024, artículo 2, página 1. |

En el primer intento histórico, la selección por grupo de herramientas
permitió que Copilot usara la conexión anterior y se abstuviera. Los
prompts finales referencian la herramienta exacta en el encabezado y en
el cuerpo. Se comprobó el servidor elegido en cada llamada del chat.
