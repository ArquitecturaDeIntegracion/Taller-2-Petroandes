# Validación de PetroAndes hasta F10 con Docker dev

Abre PowerShell en `implementacion_escenario_a` y abre Docker Desktop en modo
Linux. Ejecuta las líneas por separado en la misma terminal. Conserva el
corpus en la carpeta padre del proyecto.

## 1. Construir y ejecutar el ensayo

```powershell
docker.exe compose --profile dev build dev
docker.exe compose --profile dev run --rm -T dev tools/preflight.py
```

El inventario debe mostrar 19 PDF, 19 Markdown de contraste y `errors: []`.
Si el volumen de modelos es nuevo, prepara E5 una vez.

```powershell
$modelo = 'reports/portable/f10-e5-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json'
docker.exe compose --profile dev run --rm -T dev tools/f0.py e5 --output $modelo
```

```powershell
$salida = 'reports/portable/f10-validacion-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker.exe compose --profile dev run --rm -T dev tools/f10_check.py --output-dir $salida
```

El ensayo trabaja con un catálogo y un corpus temporales. Tarda unos minutos
porque construye varias colecciones Qdrant con el modelo E5 local.
Cuando termine, abre el resumen y la carpeta de evidencias.

```powershell
Get-Content -LiteralPath (Join-Path $salida 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json | ConvertTo-Json -Depth 8
Invoke-Item -LiteralPath $salida
```

Espera código de salida `0`, `status: passed`, **19 documentos**, **58 fragmentos
publicados al inicio**, revisión inicial **13**, revisión final **17** y
**0 eventos pendientes**. Las revisiones 14 a 17 corresponden a decisiones
o cambios técnicos en la copia desechable.

| Evidencia | Resultado esperado |
| --- | --- |
| `consolidacion.json`, `consolidacion-manifiesto.json` | La publicación inicial confirma 13 eventos. Repetirla conserva la generación y confirma cero eventos nuevos. |
| `vencimiento-tres-rutas.json`, `vencimiento-propagado.json` | El vencimiento surte efecto sin cambiar la revisión. La búsqueda se abstiene y la obtención directa y expansión se deniegan. La publicación posterior queda vacía. |
| `revocacion-en-consulta.json`, `vector-revocado.json` | Una revocación durante la búsqueda produce `gobierno_cambio`. El punto revocado sigue físicamente presente en la colección anterior. |
| `fallo-activacion.json`, `recuperacion.json` | Tres intentos fallidos conservan el puntero anterior y el evento pendiente. Tras el fallo antes de confirmar, el reintento reutiliza la generación verificada y confirma una sola vez la revisión 14. |
| `replay-14.json`, `replay-1.json` | Tanto el duplicado como el evento antiguo devuelven `evento_ya_confirmado`. |
| `aprobacion.json`, `permisos-propagados.json` | La reaprobación simulada vuelve consultable la ficha. Un cambio de permisos bloquea las tres rutas para el documento afectado y reutiliza los vectores restantes. |
| `huellas-pdf.json`, `huella-pendiente-despues.json` | El hash cambiado en la copia queda pendiente y no hereda autorización. La huella del original permanece intacta. |
| `reindexacion.json`, `rollback-*.json` | Se compara la colección reconstruida con su referencia. La reversión de la misma revisión es válida. Una generación anterior o con permisos vencidos se rechaza. |

`summary.json` compara cinco consultas calientes, una revocación y una
aprobación con las metas de 3.1. La revocación mide desde el retorno del
commit hasta que se descarta la consulta en curso. La aprobación mide desde
el commit hasta la primera recuperación exitosa. Son mediciones del equipo
de prueba y excluyen el tiempo de revisión humana.

## 2. Ejecutar la regresión y repasar fases anteriores

```powershell
docker.exe compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider
```

Espera **180 pruebas aprobadas**. Los controles nuevos verifican que la
sustitución y su evento se confirmen juntos, y que un fallo al materializar
una colección elimine solo la colección incompleta.

Las guías previas permiten repetir la [validación hasta F7](validacion-dev-hasta-f7.md),
la [evaluación técnica de F8](validacion-dev-f8.md) y el [ensayo de ataque F9](validacion-dev-f9.md).
Para la demostración en clase siguen disponibles [Inspector web](inspector-web.md)
y [Copilot](copilot-vscode.md).

## 3. Administrar una copia del laboratorio

`tools/f10.py` expone `consolidar`, `propagar`, `registrar-pdf`, `decision`,
`sustituir`, `reindexar` y `revertir`. Los comandos mutantes usan el catálogo
del perfil indicado y requieren la revisión actual. Usa un directorio de
artefactos separado y un destino de informes nuevo para cada ejecución.
Consulta el [procedimiento administrativo F10](f10-operacion.md) para
preparar la copia y ver los formatos y comandos.
