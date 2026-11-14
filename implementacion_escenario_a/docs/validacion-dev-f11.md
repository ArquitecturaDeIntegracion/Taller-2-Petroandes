# Validación integral hasta F11 en Docker dev

Para la presentación actual con una conexión `petroandes`, usa la
[guía de Inspector](inspector-web.md) y [Copilot](copilot-vscode.md).
Este ensayo integral conserva sus contextos históricos aislados.

Abre Docker Desktop en modo Linux y PowerShell en `implementacion_escenario_a`.
Conserva el corpus y los documentos del taller en la carpeta padre. Ejecuta
cada línea por separado en la misma terminal.

## 1. Preparar un proyecto Docker aislado

```powershell
$fecha = Get-Date -Format 'yyyyMMdd-HHmmss'
$proyecto = "petroandes-f11-$fecha"
$salida = "reports/portable/f11-validacion-$fecha"
docker.exe compose -p $proyecto --profile dev build dev
docker.exe compose -p $proyecto --profile dev run --rm -T dev tools/f0.py e5 --output "$salida-modelos/e5.json"
docker.exe compose -p $proyecto --profile dev run --rm -T dev tools/f0.py laya --output "$salida-modelos/laya.json"
```

Las dos sondas deben devolver `status: passed`. Esta preparación requiere
conexión para descargar las revisiones fijadas de los modelos. En ese mismo
proyecto Docker puedes reutilizar la caché al repetir la validación con un
nuevo valor de `$salida`. El perfil `dev` usa los pesos de su volumen y los
derivados de este ensayo se crean en una carpeta temporal.

## 2. Ejecutar y comprobar el resumen

```powershell
docker.exe compose -p $proyecto --profile dev run --rm -T -w /tmp dev /workspace/implementacion_escenario_a/tools/f11_check.py --output-dir $salida
```

La consola indica la etapa activa. Las pruebas se ejecutan en serie para
liberar memoria y cerrar Qdrant local entre procesos. Espera varios minutos
antes de abrir el informe.

```powershell
Get-Content -LiteralPath (Join-Path $salida 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json | ConvertTo-Json -Depth 8
Invoke-Item -LiteralPath $salida
```

| Evidencia | Resultado esperado |
| --- | --- |
| `summary.json` | `status: passed`, `cwd: ${TMPDIR}`, artefactos inicialmente ausentes y originales verificados sin cambios. |
| `baseline/reconstruccion.json` | 19 PDF producen 92 fragmentos. Catálogo en revisión 1 con 4 excluidos, 15 pendientes y 0 certificados. Se publican 0 fragmentos. La consulta se abstiene y la lectura directa de PRO-MED-007 v1 se deniega. |
| `comandos/regresion/` | 180 pruebas aprobadas y código 0 en el recibo. |
| `f7/summary.json` | Inspector lista `buscar_documentos` y `obtener_fragmento`. Se verifican las salidas, los errores de parámetros y la reapertura de 58 puntos. |
| `f8/summary.json` | Cuatro controles diagnósticos, con resultados de respaldo, pertinencia, desviación y paridad Python/MCP. |
| `f9/summary.json` | El anexo llega al compositor y queda descartado. La obtención de auditoría lo devuelve marcado como dato no confiable. |
| `f10/summary.json` | Revisión 13 → 17 y 0 eventos pendientes. Se prueban revocación, reintentos y reversión controlada. |
| `entrega/` | Manifiesto de archivos, licencias declaradas y estado de las 24 fichas de evaluación congeladas. |

Un `status: passed` se refiere a la reproducción técnica. El campo
`evaluacion_formal.ejecutada` debe ser `false` en esta reproducción técnica.
Consulta `comandos/<etapa>/command.json` y los archivos
`stdout-*.log` y `stderr-*.log` para diagnosticar un fallo.

## 3. Validar la interacción y preparar la sustentación

Usa [Inspector web](inspector-web.md) o [Copilot](copilot-vscode.md) para
repetir las consultas del laboratorio. La guía de
[F7](validacion-dev-hasta-f7.md) explica la conexión por stdio y los
contratos. La guía de [F10](validacion-dev-f10.md) muestra los estados
antes y después de propagar un cambio.

1. Formula una pregunta nueva y muestra qué documento, versión, sección y
   página respaldan la respuesta. Si se abstiene, explica qué evidencia falta.
2. Intenta obtener PRO-MED-007 v1 y muestra la denegación. Explica dónde
   se registra la sustitución y cómo la usa el catálogo.
3. Compara las listas densa, léxica y exacta en las trazas. Explica por qué
   una coincidencia alta en cualquiera de las ramas no concede vigencia.
4. Abre `f10/revocacion-en-consulta.json` y `f10/vector-revocado.json`.
   Explica cómo puede seguir presente un vector sin que la consulta devuelva
   el documento y qué comprueba una reversión.

## 4. Verificar la revisión confirmada y sus copias

Ejecuta cada línea desde la carpeta de implementación, con Docker Desktop activo.
La primera valida la versión congelada. La segunda reconstruye los catálogos
aislados con sus contextos a partir de las copias archivadas de gobierno.

```powershell
docker compose --profile dev run --rm -T dev tools/review_frozen.py
$copias = 'reports/portable/contextos-revisados-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker compose --profile dev run --rm -T dev tools/review_seed_contexts.py --output-dir $copias
Get-Content -LiteralPath (Join-Path $copias 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
```

| Qué comprobar | Resultado esperado |
| --- | --- |
| Fichas y fuentes | `passed`, ocho de ajuste, dieciséis de reserva, 43 fichas originales íntegras y 82 referencias a PDF verificadas. |
| Copias aisladas | 24 catálogos, 25 contextos. R16 tiene un contexto de auditoría y otro histórico. Cada copia tiene sus propias rutas de índice. |
| Permisos documentales | El recibo de registro muestra revisión 13 → 15, dos permisos nuevos para lectura histórica y D03 pendiente. El control de baseline devuelve `baseline_identico: true`. |
| Ejecución formal | `casos_ejecutados: 0`. Las publicaciones de los índices de caso corresponden a la evaluación posterior. |

Los recibos de la aplicación, la propagación y las copias se encuentran en la
[evidencia de cierre](../evidence/revision/20261108-confirmada/README.md).
Para el paso posterior, el [protocolo congelado](revision/20261108-confirmada/protocolo.json)
describe el reloj de cada copia, la publicación y los controles sintéticos.
