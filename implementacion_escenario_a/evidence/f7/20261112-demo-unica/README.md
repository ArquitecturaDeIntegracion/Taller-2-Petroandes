# Validación de la conexión única de PetroAndes

Fecha local: 2026-11-12, America/Bogota. Ejecución técnica: Codex.
Alcance autorizado: una conexión de presentación, Inspector, VS Code y tres Word.

## Docker dev

Se construyó `petroandes-educativo:local` con
`docker compose --profile dev build dev`, salida 0. La imagen produjo el
manifiesto `sha256:d22dc78dc5a6ffff8f782a9ed5ca27f051a84b9b2d629d391a0ea7355ff8eaad`.

La sesión SDK real ejecutó
`docker compose --profile dev run --rm -T dev tools/demo_check.py --output-dir reports/portable/demo-unica-20261112/sdk`.
Terminó con salida 0, revisión 15 y nueve comprobaciones aprobadas:
P-101 buscado y obtenido, incertidumbre, versión excluida, manual pendiente,
presión actual, firmware legítimo, contención del anexo y top_k inválido.
[Resumen](sdk/summary.json) y [llamadas originales](sdk/llamadas-001.jsonl).
La huella del snapshot se conservó antes y después.

MCP Inspector real 2.13.0 ejecutó
`docker compose --profile dev run --rm -T dev tools/demo_inspector_check.py --output-dir reports/portable/demo-unica-20261112/inspector`.
Salida 0: listado de las dos herramientas, respuesta P-101, denegación de
PRO-MED-007 v1 y abstención ante el anexo. [Resumen](inspector/summary.json).
Cada carpeta conserva comando exacto, stdout y stderr de la llamada.

La suite completa ejecutó
`docker compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider`.
Resultado observado: **180 passed in 231.28s**, salida 0. No se ejecutaron
los ocho casos formales de ajuste ni los dieciséis de reserva.
[Recibo de regresión](regresion.md).

La lectura de `petroandes.catalog status --profile baseline` en Docker dev
conservó revisión 1, 19 documentos, cuatro excluidos, quince pendientes,
cero certificados y cero decisiones registradas. El nuevo adaptador solo
escribe sus derivados en directorios temporales; no aplica decisiones.
[Lectura de baseline](baseline/command.json) y
[preflight Docker](preflight/command.json), ambos con salida 0.
Preflight confirmó fuentes íntegras, 19 PDF, `errors: []` y `warnings: []`.

## Clientes

Inspector web fue recreado con
`docker compose --profile inspector up -d --force-recreate inspector-web`.
El servicio quedó Up y `http://127.0.0.1:6274/` respondió HTTP 200.
El navegador mostró una sola entrada `petroandes`, cuyo comando es
`/usr/local/bin/python -m petroandes.demo`.
Se conectó, negoció MCP 2025-11-25 y listó ambas herramientas. La búsqueda
P-101 desde la web devolvió `respondida`, revisión 15, 1.180 psi y 1.240 psi,
con cita a la ficha v2, sección 2, página 1. La llamada tardó 36.665 ms.
[Captura del resultado web](inspector-web.png).

VS Code mostró únicamente una entrada PetroAndes: `petroandes`.
Se inició mediante MCP List Servers y Start Server. Copilot ejecutó una
búsqueda del límite de incertidumbre, con top_k 3 y filtro tipo resolucion.
La respuesta observada fue `respondida`, revisión 15, límite 0,3 % y cita a
RES-CREG-0043-2024, artículo 2, página 1; duración indicada por el cliente
1 min 35 s. Se abrió el detalle de la llamada y se comprobó que correspondía
a `buscar_documentos – petroandes (MCP Server)`, con los argumentos previstos
y salida `respondida`. [Captura de Copilot](copilot.png).

## Documentos

Se actualizaron los tres Word solicitados en `output/doc/`, carpeta hermana
de la aplicación. Se renderizaron con Microsoft Word y el rasterizador de
la habilidad de documentos; se inspeccionaron las trece páginas PNG.
Resumen ejecutivo: cuatro páginas. Diagramas: cuatro páginas.
Guía de pruebas: cinco páginas. Las versiones anteriores están en
`output/doc/versiones/20261111-antes-mcp-unico/` de la raíz del taller.
[Huellas y páginas de los Word](documentos.json).

La demostración usa el snapshot aprobado de revisión 15 y un reloj histórico
explícito del 8 de noviembre. El período real de los permisos no se amplía.
Los ensayos F9/F10 conservan sus propios contextos aislados y revisiones.
La evaluación académica formal continúa pendiente.
