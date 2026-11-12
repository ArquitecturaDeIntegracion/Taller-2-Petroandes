# Matriz de trazabilidad hasta F11

Responsable técnico: Codex. Fuente: plan, sección 9.
La [validación integral](validacion-dev-f11.md) reproduce los controles
técnicos. La columna Estado conserva los requisitos académicos pendientes.

| ID | Tareas y prueba prevista | Evidencia actual | Estado |
| --- | --- | --- | --- |
| R01 | F0/F3/F4: 19 PDF, extracción e índice persistente | [Ingesta](f3-ingesta.md) · [Índices](f4-indices.md) | 92 fragmentos extraídos y 58 puntos reabiertos en contexto histórico. |
| R02 | F1/F2: contratos, hash, autoridad, período y ámbitos | [Catálogo F2](f2-gobierno.md) · [Decisiones registradas](certificacion-laboratorio-20261103.md) | Baseline con cuatro exclusiones y quince pendientes. Doce decisiones simuladas en laboratorio. |
| R03 | F3/F4/F10: E5 fijado, tokens, trazas y reindexación | [Bundle](f4-indices.md) · [Reindexación](../evidence/f10/20261108/final/reindexacion.json) | Reconstrucción comparada dentro del bundle fijado. |
| R04 | F5: ambas ramas restringidas antes del ranking | [Recuperación gobernada](f5-recuperacion.md) | Prefiltro y revalidación, incluidos accesos directos. |
| R05 | F7: búsqueda y obtención con esquemas y errores | [Contratos MCP](f7-mcp.md) | Ambas herramientas implementadas y verificadas. |
| R06 | F0/F7/F11: Inspector, listado, llamadas y errores | [Validación F7](validacion-dev-hasta-f7.md) | Negociación, esquemas, resultados, errores y reapertura con Inspector real. |
| R07 | F1/F8: al menos 15 esperados revisados y métricas | [Propuestas](revision/README.md) · [Diagnóstico](../evidence/f8/20261108/summary.json) | Cuatro controles diagnósticos ejecutados. Calibración y reserva formal pendientes. |
| R08 | F6/F8: extracción, citas, ámbitos y abstención | [Composición](validacion-dev-hasta-f6.md) · [Diagnóstico](validacion-dev-f8.md) | Citas, abstenciones y paridad comprobadas en ensayos técnicos. |
| R09 | F9: recuperar anexo y demostrar contención o fallo | [Evidencia del ataque](../evidence/f9/20261108/summary.json) | Recuperación, descarte y auditoría autorizada comprobados. |
| R10 | F10/F11: cambios, revocación, fallos y reproducción | [Propagación](../evidence/f10/20261108/final/summary.json) · [Reproducción](validacion-dev-f11.md) | Revocación con punto presente, idempotencia, reintentos y reversión verificados. |

## Revisión académica pendiente

El estudiante o grupo debe revisar cada esperado contra sus páginas PDF y
registrar quién revisó qué. El perfil de laboratorio vincula cada decisión a
SHA-256, uso, ámbito, acceso e intervalo efectivo. El diagnóstico técnico y
las certificaciones simuladas registradas tienen evidencias separadas.
