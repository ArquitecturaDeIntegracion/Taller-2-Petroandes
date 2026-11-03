# Matriz inicial de trazabilidad

Fecha: 2026-11-01. Responsable técnico: Codex. Fuente: plan, sección 9.
Ningún requisito global se considera completo con la base técnica actual de F0–F3.

| ID | Tareas y prueba prevista | Evidencia actual | Estado |
| --- | --- | --- | --- |
| R01 | F0/F3/F4: 19 PDF, extracción e índice persistente | [19 PDF y fragmentos F3](f3-ingesta.md) | Extracción verificada; índice F4 pendiente |
| R02 | F1/F2: contratos, hash, autoridad, período y ámbitos | [Catálogo y controles F2](f2-gobierno.md) | Cuatro exclusiones, quince pendientes; revisión humana pendiente |
| R03 | F3/F4/F10: E5 fijado, tokens, trazas y reindexación | [Partición y tokenizador reales F3](f3-ingesta.md) | 92 fragmentos y reingesta estables; indexación/reindexación pendientes |
| R04 | F5: ambas ramas restringidas antes del ranking | [Política común F2](f2-gobierno.md) | Elegibilidad probada; ramas del recuperador pendientes |
| R05 | F7: búsqueda y obtención con esquemas y errores | [Contratos iniciales](contratos.md) | Implementación pública pendiente |
| R06 | F0/F7/F11: Inspector, listado, llamadas y errores | [Inspector real](../evidence/f0/mcp-local/summary.json) | F0 verificado; F7/F11 pendientes |
| R07 | F1/F8: al menos 15 esperados revisados y métricas | [Calidad](../knowledge/05-calidad.md) | Revisión humana pendiente |
| R08 | F6/F8: extracción, citas, ámbitos y abstención | Diseño acordado | Pendiente |
| R09 | F9: recuperar anexo y demostrar contención o fallo | [Anexo extraído y marcado en F3](f3-ingesta.md) | Conservación verificada; recuperación/ataque F9 pendientes |
| R10 | F10/F11: cambios, revocación, fallos y reproducción | [Revisión/eventos F2](f2-gobierno.md) | Transacción y rollback de autorización probados; propagación y reproducción pendientes |

## Revisión académica pendiente

El estudiante o grupo debe identificar responsable, rol representado y revisar
cada decisión simulada y cada esperado contra sus páginas PDF. No se infiere
aprobación por ejecutar pruebas sintéticas. Baseline: cuatro excluidos,
quince pendientes y cero certificados positivos.

El perfil académico deberá estar separado del baseline, vincular cada decisión
a SHA-256, uso, ámbito, acceso e intervalo efectivo y rotular toda simulación.
La selección de casos reservados no se usará para ajustar recuperación.
