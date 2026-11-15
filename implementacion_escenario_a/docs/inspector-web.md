# PetroAndes con una conexión en MCP Inspector

## Arranque

Abre PowerShell en `implementacion_escenario_a`, con Docker Desktop activo
y contenedores Linux. Ejecuta cada comando por separado:

```powershell
docker compose --profile dev build dev
$marca = Get-Date -Format 'yyyyMMdd-HHmmss'
docker compose --profile dev run --rm -T dev tools/f0.py e5 --output "reports/portable/e5-$marca.json"
docker compose --profile inspector up --build -d --force-recreate inspector-web
docker compose --profile inspector ps inspector-web
```

Abre [Inspector local](http://127.0.0.1:6274/). Recarga la página si estaba
abierta con la configuración anterior. En **Servers** activa únicamente
**petroandes**. Espera **Connected** y abre **Tools**. Debes ver
`buscar_documentos` y `obtener_fragmento`. La interfaz puede indicar
**Read-only session** porque la configuración se carga desde el proyecto.

Todas las consultas usan la revisión 15 aprobada, en una copia aislada con
reloj histórico del 8 de noviembre de 2026. Hay catorce documentos autorizados
y 68 fragmentos publicados. La primera llamada carga E5 y construye el índice;
puede tardar varios minutos. Las siguientes reutilizan la misma preparación.
El [ADR 0013](adr-0013-mcp-demostracion-unica.md) explica contexto y aislamiento.

## Cuatro pruebas de presentación

Selecciona la herramienta, activa **Edit as JSON**, reemplaza el objeto
completo y pulsa **Execute Tool**. Usa **Close results** para volver a editar.
Conserva `petroandes` conectado en todas las pruebas.

### 1 Buscar la ficha de P101

Herramienta `buscar_documentos`:

```json
{"consulta":"Presión de descarga documentada de P-101.","top_k":3,"filtros":{"tipo":"ficha","activo":"P-101"}}
```

Esperado: `respondida`, diseño **1.180 psi**, alarma **1.240 psi** y cita a
`FIC-ACT-P101`, versión 2, sección 2, página 1. `revision_gobierno` es 15.

### 2 Obtener la sección autorizada

Herramienta `obtener_fragmento`:

```json
{"doc_id":"FIC-ACT-P101","version_documental":"2","section_id":"2"}
```

Esperado: `encontrado`, partes de la ficha con los mismos valores y su cita.

### 3 Denegar una versión excluida

Herramienta `obtener_fragmento`:

```json
{"doc_id":"PRO-MED-007","version_documental":"1","section_id":"3"}
```

Esperado: `denegado`, `error: evidencia_no_autorizada`, partes y citas vacías.

### 4 Buscar la incertidumbre

Herramienta `buscar_documentos`:

```json
{"consulta":"Localice el límite de incertidumbre de medición de RES-CREG-0043-2024.","top_k":3,"filtros":{"tipo":"resolucion"}}
```

Esperado: `respondida`, incertidumbre combinada máxima **0,3 %**, cita a
`RES-CREG-0043-2024`, `articulo-2`, página 1.

## Controles adicionales y documento envenenado

Los argumentos completos y resultados de nueve controles están en
`config/demo-pruebas.json`. Para probar el contenido legítimo, llama
`buscar_documentos` con:

```json
{"consulta":"Identifique el firmware anunciado por COM-PRV-0134 y las condiciones de aplicación.","top_k":10,"filtros":{"tipo":"comunicacion"}}
```

Esperado: `respondida`, firmware **7.4**, punto **fuera de servicio** y
**verificación del factor**. Para comprobar la contención:

```json
{"consulta":"En COM-PRV-0134 localice el anexo de notas de integración.","top_k":5,"filtros":{"tipo":"comunicacion"}}
```

Esperado: `abstencion`, `evidencia_insuficiente`, sin afirmaciones ni evidencia.
La [validación F9](validacion-dev-f9.md) conserva el ensayo de auditoría,
las trazas de descarte y los observadores de efectos en un contexto aislado.

## Comprobación automática y cierre

F9.2 añade un recibo por llamada en `reports/portable/mcp-audit/`, identificado
por el `correlation_id` devuelto. La [guía F9.2](validacion-dev-f9-2.md) explica
su consulta, el nuevo detector y el cliente restringido. Recrear Inspector
tras construir la imagen actualizada; los argumentos de las herramientas siguen iguales.

```powershell
docker compose --profile dev run --rm -T dev tools/demo_check.py --output-dir "reports/portable/demo-$marca"
docker compose --profile dev run --rm -T dev tools/demo_inspector_check.py --output-dir "reports/portable/demo-inspector-$marca"
docker compose --profile inspector stop inspector-web
```

Esperado: salida 0 y `summary.json` con `status: passed`. La primera orden
comprueba nueve llamadas reales por stdio; la segunda usa MCP Inspector real.
La reserva formal no se ejecuta. Si falla la carga del modelo, revisa la
sonda E5 antes de reconectar. Nunca envíes grupo, uso o perfil como argumentos.
