# Validación de PetroAndes hasta F9 con Docker dev

Abre Docker Desktop en modo contenedores Linux y PowerShell en la carpeta
`implementacion_escenario_a`. Conserva el corpus PDF en la carpeta padre del
proyecto. Ejecuta las líneas de PowerShell por separado en la misma terminal.

## 1. Construir y comprobar la base

```powershell
docker.exe compose --profile dev build dev
docker.exe compose --profile dev run --rm -T dev tools/preflight.py
```

Espera 19 PDF, 19 Markdown de contraste y `errors: []`. Si el volumen de
modelos es nuevo, carga E5 con el siguiente comando y espera `status: passed`.

```powershell
$modelo = 'reports/portable/f9-e5-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json'
docker.exe compose --profile dev run --rm -T dev tools/f0.py e5 --output $modelo
```

```powershell
docker.exe compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider
```

Espera que las 178 pruebas pasen. Para repetir las comprobaciones previas,
sigue la [validación hasta F7](validacion-dev-hasta-f7.md) y la
[validación de F8 con laya](validacion-dev-f8.md). Para probar el cliente en
clase, usa la [guía web del Inspector](inspector-web.md) o las
[cuatro preguntas de Copilot](copilot-vscode.md).

## 2. Ejecutar el ensayo F9

```powershell
$salida = 'reports/portable/f9-docker-dev-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker.exe compose --profile dev run --rm -T dev tools/f9_attack.py --output-dir $salida
```

El ensayo puede tardar unos minutos porque reconstruye los índices temporales
y abre un proceso MCP por llamada de Inspector. Cuando termine el contenedor,
lee el informe con otra línea de PowerShell.

```powershell
$resumen = Get-Content -LiteralPath (Join-Path $salida 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$resumen | ConvertTo-Json -Depth 8
```

Espera código de salida `0`, `status: passed`, revisión de gobierno `13` y
todas las comprobaciones en `true`. Usa una nueva carpeta en cada intento.
Si el comando falla, revisa `summary.json` y los recibos y transcripciones
de Inspector que alcanzó a guardar esa corrida.

| Evidencia | Resultado esperado |
| --- | --- |
| `anexo.json` | COM-PRV-0134, sin versión, sección `anexo-notas-de-integracion`, página 1. Registra SHA-256 del PDF y del texto extraído, marca `instrucciones_dirigidas_al_procesador` y referencia a la decisión académica. |
| `recuperacion/` | La consulta «En COM-PRV-0134 localice el anexo de notas de integración» recupera el fragmento íntegro. Los archivos de las ramas muestran candidatos y `traza.json` conserva la selección. |
| `ataque/` | `buscar_documentos` devuelve `abstencion` con `evidencia_insuficiente`, sin afirmaciones ni citas. El mismo ID del anexo aparece en `descartados_seguridad`. |
| `anexo-directo/` | `obtener_fragmento` devuelve `encontrado`, el texto íntegro y la marca `contenido_no_confiable: true` bajo el uso `inspeccion_no_confiable`. |
| `firmware/` | `buscar_documentos` devuelve `respondida`. Cita firmware **7.4**, una ventana con el punto de medición fuera de servicio y la verificación posterior del factor del medidor. |
| `summary.json` | Las tres llamadas coinciden entre Python e Inspector, salvo el identificador de correlación. El catálogo conserva la misma huella antes y después. Los observadores registran cero intentos durante las consultas. |

## 3. Interpretar el resultado

F5 recupera el anexo con los filtros habituales del contexto histórico. F6
identifica su marca de seguridad antes de seleccionar extractos. El uso
`inspeccion_no_confiable` tiene una publicación temporal propia y permite
leer el anexo como dato de auditoría. Se utiliza la decisión académica ya
registrada para COM-PRV-0134 y el reloj de esa simulación. El ensayo trabaja
con una copia temporal del catálogo y abre el catálogo de esa copia en modo
lectura durante las consultas.

La lista MCP contiene solo `buscar_documentos` y `obtener_fragmento`. Los
observadores de Python interceptan eventos de red, ejecución de procesos y
accesos a archivos con `balance` en su nombre. Las sondas positivas emplean
eventos sintéticos y un archivo ficticio. La comprobación cubre las rutas
Python y MCP ejecutadas en el ensayo. Un cliente LLM que reciba el anexo de
auditoría debe aplicar sus propios controles al consumirlo.
[Evidencia de la corrida de referencia](../evidence/f9/20261108/).
