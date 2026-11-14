# ADR 0013 Una conexión MCP para la presentación

Fecha: 2026-11-12. Estado: implementado por solicitud de Jonnathan Caballero.

## Decisión

Inspector y VS Code muestran una sola conexión, `petroandes`, con las dos
herramientas de lectura existentes. Ejecutan `python -m petroandes.demo`.
No es necesario cambiar de servidor entre las consultas de la presentación.

El adaptador reutiliza el servicio F5/F6 y los contratos F7. La configuración
`config/mcp-demo.json` fija el snapshot aprobado de revisión 15, su SHA-256,
el grupo `LAB_REVISION`, el ámbito `general:corpus_revision` y el uso
`evidencia_historica`. El reloj histórico es
`2026-11-08T22:34:26.021685-05:00`, fecha de la aprobación registrada.
Esta elección reproduce la decisión académica sin ampliar sus fechas efectivas.
No representa el estado documental en tiempo real ni una autorización productiva.

Cada proceso copia el snapshot y construye un catálogo e índice privados en
un directorio temporal. Verifica revisión, huella, 14 documentos autorizados
y 68 fragmentos publicados, a partir de 19 PDF y 92 fragmentos de ingesta.
La primera llamada prepara E5 y los índices; al cerrar se liberan los datos
temporales. Cada cliente tiene su propio proceso del mismo servidor lógico,
lo que evita compartir simultáneamente un almacenamiento Qdrant local.

## Configuración y controles

`.vscode/mcp.json` contiene solo `servers.petroandes`. `.mcp.json` queda sin
entradas para evitar la importación duplicada del mismo servidor en VS Code.
`config/inspector-web.json` declara solo `petroandes`; la web sigue en 6274.
El lanzador web ya no prepara una segunda conexión histórica F7.

En la conexión única funcionan las respuestas de P-101, incertidumbre y
firmware. Los controles negativos usan PRO-MED-007 v1 excluido, MAN-OPE-004
v2 pendiente, presión actual fuera del corpus y descarte del anexo malicioso.
Las antiguas denegaciones de la ficha P-101 en el contexto habitual pasan a
ser respuestas autorizadas en esta demostración. Los cuatro prompts se
actualizan con estos escenarios y con el mismo nombre de conexión.

Los argumentos públicos no permiten elegir grupos, usos, reloj ni perfil.
La inspección especial del anexo se mantiene en el arnés aislado F9. Los
cambios de gobierno se comprueban con F10. Estas tareas no requieren añadir
otra conexión visible ni cambiar los permisos del servidor de presentación.

## Consecuencias y verificación

El catálogo persistido, baseline y las fuentes originales se conservan.
Los arneses históricos F7 a F10 siguen disponibles y mantienen sus revisiones
de prueba documentadas. No se ejecutan los casos formales de ajuste o reserva.
Un cambio del corpus o del snapshot rompe la comprobación de integridad;
requiere una revisión explícita de esta configuración.

`tools/demo_check.py` comprueba nueve llamadas con el SDK MCP real por stdio.
`tools/demo_inspector_check.py` comprueba listado, respuesta, denegación y
contención con Inspector real. La evidencia y las observaciones de los
clientes se conservan en `evidence/f7/20261112-demo-unica/`.
Las guías [web](inspector-web.md) y [Copilot](copilot-vscode.md) son la
referencia actual. Los documentos y recibos históricos conservan su contexto.
