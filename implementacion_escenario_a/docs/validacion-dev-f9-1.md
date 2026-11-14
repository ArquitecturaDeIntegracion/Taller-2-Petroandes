# Validar el arnés F9 ampliado en Docker dev

Ejecutar en PowerShell desde `implementacion_escenario_a`.
Se conserva el servidor único `petroandes` de Inspector y VS Code.
Estas pruebas automáticas del arnés no requieren abrir sus interfaces web.

## Preparar la imagen y los pesos

Docker Desktop debe estar iniciado con contenedores Linux.

```powershell
docker compose --profile dev build dev
docker compose --profile dev run --rm -T dev tools/preflight.py
```

Esperado: imagen construida, fuentes originales con hashes coincidentes y
19 PDF. Si el volumen de modelos aún no está preparado, descargar y comprobar
E5 en el mismo proyecto Docker antes de aislarlo:

```powershell
$modelo = 'reports/portable/f9-e5-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json'
docker compose --profile dev run --rm -T dev tools/f0.py e5 --output $modelo
```

Esperado: `status = passed`. Esta preparación inicial requiere conexión.
El ensayo aislado usa los pesos existentes de `model-cache` en solo lectura
y no descarga modelos. La [guía F11](validacion-dev-f11.md) documenta además
la preparación integral en un proyecto Docker separado; sus volúmenes no
son automáticamente los del proyecto Docker habitual.

## Ejecutar la validación completa

El controlador necesita Python del proyecto y Docker en el PATH del host.
No se ejecuta dentro de un contenedor ni necesita montar el socket Docker.
Enviar cada línea como un comando separado, sin envolver el bloque en `if`.

```powershell
$salida = 'reports/portable/f9-guard-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
.\.venv\Scripts\python.exe tools/f9_validate.py --output-dir $salida
$LASTEXITCODE
Get-Content (Join-Path $salida 'summary.json') -Raw | ConvertFrom-Json
```

Esperado: código `0`, `status = passed`, tres verificaciones en `verified`,
`pending = []` y `cleanup_completed = true`. Puede tardar varios minutos:
reingiere los PDF, publica índices temporales y hace llamadas Inspector reales.
El límite configurable por ensayo es `--timeout 1800`, expresado en segundos.
Usar siempre una carpeta nueva; una carpeta existente se rechaza.

## Revisar qué se comprobó

```powershell
Get-Content (Join-Path $salida 'sandbox-probe.json') -Raw | ConvertFrom-Json
Get-Content (Join-Path $salida 'ensayo/summary.json') -Raw | ConvertFrom-Json
Get-Content (Join-Path $salida 'ensayo/frontera_consumidor/summary.json') -Raw | ConvertFrom-Json
```

| Evidencia dentro de la carpeta de salida | Resultado esperado |
| --- | --- |
| `network-positive.json` | Conexión nativa al receptor ficticio y marcador F9_CONTROL. |
| `sandbox-configuration.json` | Todas las comprobaciones de configuración efectiva verdaderas. |
| `sandbox-probe.json` | UID 10001, escrituras denegadas, sin capacidades, red sin ruta al mismo receptor. |
| `ensayo/f9_original/resultado/summary.json` | Anexo recuperado íntegro, descartado en composición y disponible como dato de auditoría; firmware 7.4 con condiciones y citas. |
| `ensayo/fronteras_mcp/resultado/summary.json` | Permisos adicionales inválidos; hash ajeno, excluido y pendiente denegados sin evidencia; contextos separados. |
| `ensayo/frontera_consumidor/summary.json` | 23 casos aprobados: 18 adversariales y 5 benignos; sin efectos, filtración o contaminación indebidos. |
| `ensayo/summary.json` | Tres fases aprobadas, fuentes y reserva intactas, LLM real no evaluado. |

Los archivos `casos-*.jsonl`, `eventos-*.jsonl` y `resultados-*.jsonl`
conservan entradas, recibos del cliente, propuestas y decisiones por caso.
Un rechazo válido indica la capa y motivo exactos; un error no equivale a bloqueo.
El inventario protegido no ejecuta ni evalúa las fichas A/R.

## Regresión del proyecto

```powershell
docker compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider
docker compose --profile dev run --rm -T dev tools/validate_agent.py
```

Esperado: suite sin fallos y validador estructural sin errores ni archivos
textuales de más de 200 líneas. La suite de software no ejecuta la evaluación
formal congelada de reserva. No abre interfaces humanas de Copilot.

## Si algo falla o se interrumpe

Revisar `summary.json`, `commands.json` y los recibos `command.json` con
stdout/stderr por partes. Conservar esa carpeta y repetir con un nombre nuevo
después de corregir la causa. Si fallan el receptor positivo o el aislamiento,
el controlador no ejecuta el ataque ni declara éxito.
Ctrl+C solicita la interrupción; no acredita que el ensayo haya terminado.
Un cierre forzado de Python o Docker puede impedir la limpieza: revisar los
nombres y etiquetas propios en la evidencia antes de retirar recursos.
No eliminar volúmenes de modelos, artifacts ni contenedores ajenos.

El sandbox necesita iniciar procesos Python y Node para MCP por stdio.
No-new-privileges y cap_drop no equivalen a prohibir todos los subprocess.
La protección del arnés no se extiende automáticamente al IDE del usuario.
Los casos sintéticos no acreditan detección universal ni resistencia de un LLM.

[Decisión de diseño](adr-0014-arnes-f9-1.md).

## Corrida comprobada del 13 de noviembre

La imagen se construyó y la regresión pasó 232 pruebas en Docker dev.
El ensayo integrado aprobó tres fases, con 23 casos sintéticos, 24 propuestas,
18 denegaciones previstas y cinco tareas benignas completadas. La integridad
de 379 archivos protegidos permaneció igual y la limpieza se completó.
Las tres fases tardaron aproximadamente 13 minutos en este equipo; el tiempo
de otra ejecución depende de los recursos y de la caché disponible.

[Evidencia conservada](../evidence/f9/20261113-arnes-ampliado/README.md).
