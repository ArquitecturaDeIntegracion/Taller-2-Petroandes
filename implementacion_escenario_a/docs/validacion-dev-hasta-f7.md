# Validación de PetroAndes hasta F7 con Docker dev

Abre PowerShell en `implementacion_escenario_a` e inicia Docker Desktop en modo
contenedores Linux. Conserva el corpus en la raíz del taller. El perfil
`dev` monta el código local y la imagen incluye Node e Inspector.

## 1. Preparar el entorno y validar F0 a F6

```powershell
docker compose --profile dev build dev
docker compose --profile dev run --rm -T dev tools/validate_agent.py
docker compose --profile dev run --rm -T dev tools/preflight.py
```

**Esperado.** La imagen se construye, el validador termina con `OK` y el preflight
informa 19 PDF, 19 Markdown de contraste y `errors: []`.

Si el volumen de modelos es nuevo, materializa E5 una vez con red y una ruta
de salida nueva. El ensayo usa la revisión fijada y verifica la dimensión 384.

```powershell
docker compose --profile dev run --rm -T dev tools/f0.py e5 --output reports/portable/validacion-f7-e5.json
```

```powershell
docker compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider --basetemp /tmp/validacion-hasta-f7
```

**Esperado.** Pasan 178 pruebas de regresión con código 0. Incluye las
comprobaciones F5 y F6. [Ejemplos de composición y abstención F6](validacion-dev-hasta-f6.md).

## 2. Ejecutar el Inspector real

Para probar las herramientas manualmente en un navegador, sigue la
[guía del Inspector web](inspector-web.md).

Ejecuta cada línea por separado en la misma terminal PowerShell.

```powershell
$salida = 'reports/portable/validacion-f7-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker.exe compose --profile dev run --rm -T dev tools/f7_inspector.py --output-dir $salida
```

El comando genera los argumentos JSON dentro del contenedor. En la consola
espera el resumen con `status: passed`. Para volver a verlo como objeto de
PowerShell, ejecuta este comando por separado en la misma terminal.

```powershell
Get-Content -LiteralPath (Join-Path $salida 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
```

Los recibos `command.json` conservan los comandos exactos. Los archivos
`stdout-*.log` y `stderr-*.log` contienen las transcripciones. Inspector usa
stdio en modo `legacy` para el SDK fijado.

| Carpeta | Resultado esperado |
| --- | --- |
| `list` | Dos herramientas, cada una con `inputSchema` y `outputSchema`. |
| `search-ok` | `respondida` y cita de FIC-ACT-P101, versión 2, sección 2. La fila contiene 1.180 psi de diseño y 1.240 psi de alarma en el ensayo histórico. |
| `direct-ok` | `encontrado` con una parte citada de RES-CREG-0043-2024, artículo 2. La versión es `null` y el texto está marcado como no confiable. |
| `search-abstention` | `abstencion` con `sin_evidencia_autorizada` bajo el contexto habitual. |
| `direct-denied` | `denegado` con `evidencia_no_autorizada` y listas vacías para el manual pendiente. |
| `search-invalid`, `direct-invalid`, `privilege-invalid` | `isError: true` con `parametros_invalidos`. En cada recibo Inspector registra código 5, esperado en estos ensayos. |
| `index-error`, `service-error` | `indice_no_listo` y `servicio_no_disponible`, respectivamente, como estados de dominio. |
| `reconnect`, `wire` | Otra sesión devuelve la misma generación y el mismo contenido. La sonda registra la negociación, salida JSON-RPC y cierre. Los diagnósticos de prueba aparecen en stderr. |

Las llamadas positivas reingieren los 19 PDF y publican 58 fragmentos de 12
documentos en una copia temporal de revisión 13. El reloj se fija en el
instante ya autorizado dentro de la simulación académica. Los UUID de
correlación cambian en cada consulta. El ensayo compara citas, filtros y
respuestas con la llamada directa a las funciones Python.
[Contratos y estados MCP](f7-mcp.md).

## 3. Conectar un cliente al volumen habitual

Si ya tienes el catálogo del laboratorio en Docker, genera la entrada de
servidor desde la carpeta de implementación. Usa la configuración resultante
en el cliente MCP que admita conexiones stdio.

```powershell
$docker = (Get-Command docker).Source
$compose = (Join-Path (Get-Location).Path 'compose.yaml')
@{ mcpServers = @{ petroandes = @{
    command = $docker
    args = @('compose', '-f', $compose, '--profile', 'dev', 'run', '--rm',
             '-T', 'dev', '-m', 'petroandes.mcp_server', '--profile', 'laboratorio')
}}} | ConvertTo-Json -Depth 6
```

Lista las herramientas y llama a `buscar_documentos` con `consulta` igual a
`Presión de descarga documentada de P-101.`. En el volumen habitual espera
`sin_evidencia_autorizada` a revisión 13. Para `obtener_fragmento`, usa
`doc_id` igual a `FIC-ACT-P101`, `version_documental` igual a la cadena `2`
y `section_id` igual a la cadena `2`. Espera `evidencia_no_autorizada`.
Ejecuta por turnos los procesos que usen el mismo índice local.
