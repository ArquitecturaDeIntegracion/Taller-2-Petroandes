# Estado de reanudación

Actualizado el 2026-11-07, America/Bogota. Responsable técnico Codex.

## Tarea activa

F6 implementa composición extractiva determinista sobre la recuperación F5.
La operación `responder` de `tools/f5.py` devuelve `SearchResponse`, una
representación legible y una traza correlacionada. El conjunto autorizado y
la revisión se verifican después de componer, antes de devolver la respuesta.

[ADR de composición](adr-0010-composicion-f6.md) ·
[Guía de validación en Docker dev](validacion-dev-hasta-f6.md) ·
[Evidencia de F6](../evidence/f6/20261107/).

La imagen se construyó y la suite completa pasó 178 pruebas en Docker `dev`,
incluidos 22 controles de F6. Los comandos de la guía se probaron en
Windows PowerShell 5.1.

Las reglas conservan condiciones, cifras, negaciones y citas por afirmación.
Exigen ámbito para las filas de tramo o activo, anclas documentales y
secciones completas. Distinguen alarma, MAOP, especificación de activo,
incertidumbre, tolerancia, secuencia, recomendación y decisiones históricas.
La traza identifica el anexo descartado y la obtención autorizada conserva
su texto marcado como no confiable.

La prueba histórica parte de la revisión 13. Reingiere los 19 PDF y reabre
58 fragmentos de 12 documentos bajo `LAB_REVISION`, `general:corpus_revision`
y `evidencia_historica`, con el reloj controlado dentro del período aprobado.
Verifica extractos positivos, ámbito ambiguo, evidencia insuficiente,
datos fuera del corpus, conflicto y vencimiento durante la composición.
El control de MAOP usa el extractor de filas en aislamiento porque
MAN-OPE-001 sigue pendiente en el catálogo.

## Estado del despliegue y continuidad

| Perfil | Revisión | Clasificación | Respuesta en el contexto del servicio |
| --- | --- | --- | --- |
| baseline | 1 | 4 excluidos, 15 pendientes | `sin_evidencia_autorizada` |
| laboratorio | 13 | 4 excluidos, 3 pendientes, 12 certificados simulados | `sin_evidencia_autorizada` |

El contexto del servicio usa grupo `lectores-educativos`, ámbito
`general:lectura-documental-educativa` y uso `recomendacion`. Las
certificaciones simuladas tienen ámbito `general:corpus_revision`,
grupo `LAB_REVISION` y fin exclusivo 2026-12-01T00:00:00-05:00.
La obtención directa de la ficha P-101 en el contexto del servicio
devuelve `evidencia_no_autorizada`.

El [estado hasta F5](estado-hasta-f5.md) conserva el historial y las evidencias
de F0 a F5 y de la [incorporación administrativa](certificacion-laboratorio-20261103.md).
Incluye la corrección de reapertura de Qdrant y la CLI compatible con
Windows PowerShell. La guía anterior conserva las comprobaciones de
catálogo, publicación y recuperación de candidatos.
[Validación hasta F5](validacion-dev-hasta-f5.md).

## Pendientes y siguiente fase

- Los 24 casos académicos de ajuste y reserva requieren revisión humana.
  F6 se verificó con ensayos técnicos independientes. La calibración
  de reglas y los esperados académicos siguen pendientes.
- MAN-OPE-001 v3, MAN-OPE-004 v2 y MAN-MTO-002 v1 siguen pendientes.
  F2 conserva una sola huella activa por código y versión.
- El siguiente incremento técnico es F7. Conectar `answer` y la obtención
  directa a las dos herramientas MCP de lectura. Verificar stdio y las
  llamadas positivas y negativas con MCP Inspector real. Usar
  `petroandes-recuperacion-mcp` y mantener un único propietario de Qdrant.
- La evaluación formal corresponde a F8, el ensayo de ataque a F9 y
  el consumo del outbox de gobierno a F10.
