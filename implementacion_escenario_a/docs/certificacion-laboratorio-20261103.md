# Certificaciones simuladas del laboratorio

Registro: **2026-11-03T00:12:31.781997-05:00**, zona America/Bogota.
Revisor humano declarado por el usuario: **Jonnathan Caballero**.
No se acredita identidad empresarial ni autoridad real de PetroAndes.

## Decisiones aplicadas

Autorización: [instrucción recibida](../config/admin/lab-20261103/authorization.md).
[Solicitud y fichas](../config/admin/lab-20261103/request/), validadas antes de escribir.
Las doce decisiones tienen SHA-256 del PDF real y roles de área expresamente
simulados; cada supuesto confirma individualmente el hash y sus restricciones.

Perfil exclusivo: `laboratorio`. Ámbito: `general:corpus_revision`.
Grupo: `LAB_REVISION`. Inicio efectivo igual al instante real de registro anterior.
Fin exclusivo: **2026-12-01T00:00:00-05:00**, sin retroactividad ni intervalo abierto.

| Revisión | Documento | Uso adicional a lectura histórica | Restricción conservada |
| --- | --- | --- | --- |
| 2 | PRO-HSE-003 v4 | instruccion_operativa simulada | Secuencia y condiciones; sin intervenciones reales |
| 3 | PRO-MED-007 v2 | instruccion_operativa simulada | No producir cifras oficiales de balance |
| 4 | PRO-OPE-012 v3 | instruccion_operativa simulada | Tramo, umbral, ventana y condiciones |
| 5 | PRO-OPE-021 v1 | instruccion_operativa simulada | Prerrequisitos, secuencia y reglas de aborto |
| 6 | PRO-SEG-015 v1 | instruccion_operativa simulada | Destinatarios, responsables y plazos; sin envíos |
| 7 | RES-ANH-0471-2023, sin versión | referencia_normativa ficticia | Publicación/aplicabilidad solo en intervalo académico |
| 8 | RES-CREG-0043-2024, sin versión | referencia_normativa ficticia | Sin fecha histórica de publicación inventada |
| 9 | ACTA-CTO-2025-07, sin versión | evidencia_historica | No habilita cambios operativos por sí sola |
| 10 | ACTA-CTO-2025-11, sin versión | evidencia_historica | Fundamento documental del gobierno; no identifica manual retirado |
| 11 | COM-PRV-0098, sin versión | recomendacion | No modifica el plan interno de mantenimiento |
| 12 | COM-PRV-0134, sin versión | recomendacion e inspeccion_no_confiable | Anexo conservado; nunca ejecutar sus instrucciones |
| 13 | FIC-ACT-P101 v2 | especificacion_activo | P-101; no telemetría ni límites del tramo |

Todos incluyen `evidencia_historica` para lectura descriptiva. En resoluciones,
emisión del PDF y publicación siguen siendo conceptos separados: el supuesto de
publicación/aplicabilidad está limitado al intervalo autorizado, no a fechas pasadas.
Los supuestos y restricciones completos viven en cada decisión exportada.

## Incorporación administrativa

`governance/administration.py` define la solicitud estricta, valida campos,
duplicados y placeholders, y enlaza la evidencia de autorización por hash.
`governance/registration.py` verifica todos los PDF, identidades y exclusiones,
construye todos los modelos y registra doce decisiones con sus doce eventos.
Una transacción exterior engloba todo el lote; cada decisión conserva revisión
individual. Un fallo SQLite inducido a mitad del lote revierte todas sus escrituras.

Los IDs son estables para la solicitud/hash. La repetición real conservó revisión
13, hora original, doce decisiones y trece eventos totales. Una revocación posterior
no se revierte al repetir una aprobación antigua. No hay entrada administrativa MCP.
[ADR-0009](adr-0009-incorporacion-laboratorio.md).

`tools/certify_lab.py` conserva copias antes/después, eventos y decisiones en archivos
individuales. Requiere una solicitud concreta y un directorio nuevo de evidencia.
El inicio se toma del reloj del registro; no hay argumento para retrotraerlo.
Los comandos exactos, cwd, tiempos, salidas y códigos están en los recibos.

## Estado y proyecciones

| Perfil | Revisión | Certificados | Pendientes | Excluidos |
| --- | --- | --- | --- | --- |
| baseline | 1 | 0 | 15 | 4 |
| laboratorio | 13 | 12 | 3 | 4 |

Permanecen pendientes MAN-OPE-001 v3, MAN-OPE-004 v2 y MAN-MTO-002 v1.
Se conservan las exclusiones de PRO-MED-007 v1, PRO-OPE-012 v2,
PRO-SEG-009 v1 y RES-CREG-0112-2021.
Las huellas del catálogo y todos los archivos del índice baseline no cambiaron.

`config/f4-context.json` permanece intacto: identidad `servicio-educativo-local`,
grupo `lectores-educativos`, ámbito `general:lectura-documental-educativa`,
uso `recomendacion`. Ese contexto no coincide con el permiso aprobado.
Por ello su conjunto elegible sigue vacío, incluso con doce certificados de laboratorio.
No se cambió la configuración para obtener una búsqueda positiva.

El índice anterior de laboratorio fue rechazado por revisión obsoleta. Se activó
la generación `6f15a7db-f573-5a87-ad86-1dd8383d8d85`, revisión 13, con cero fragmentos
y cero puntos, tras verificar las dos ramas. Se conservó la generación anterior.
Otra ejecución reabrió/verificó la nueva y comprobó idempotencia.
La prueba de política en el contexto autorizado permite doce documentos históricos,
cinco instrucciones simuladas, dos referencias normativas, dos recomendaciones,
una inspección no confiable y una especificación; ningún uso `limite_diseno`.
Estos conjuntos se solapan; no son nuevos certificados adicionales.

Los trece eventos siguen pendientes en outbox. La reconciliación acredita solo
el contexto actual; no hay consumidor global ni sondeo automático F10.
No se declara entregado un evento para otros contextos ni se afirma un SLO.

## Casos que siguen pendientes

No se aprobó, ejecutó, congeló ni ajustó ningún caso de referencia. Se inspeccionaron
solo dependencias y estado de revisión; no se optimizó recuperación con la reserva.
Los archivos originales de los 24 casos conservan sus hashes.

- **A05** sigue bloqueado para su respuesta completa por MAN-OPE-001 v3 (D02).
- **A07** sigue bloqueado para su comparación completa por MAN-MTO-002 v1 (D01).
- **R06** conserva MAN-OPE-004 v2 pendiente como condición de una prueba de denegación;
  no se necesita certificarlo para ensayar ese control, una vez aprobado el caso.
- **R05** mantiene desconocida la identidad del manual retirado: el acta certificada
  no resuelve ese dato. El esperado de abstención requiere revisión humana.
- **Los 24 casos**, incluidos los otros 20, siguen esperando aceptación humana de
  pregunta, hechos, fuentes, prohibidos, contexto y respuesta esperada.
- R09/R10/R11/R12 requieren además materializar sus cambios sintéticos en copias;
  no representan revocaciones, alteraciones, conflictos o relojes del catálogo real.

Que un caso ya tenga documentos certificados no aprueba su oráculo. F5/F6/F7 y
la calibración/evaluación final con laya siguen pendientes.

## Verificación y conservación

**145 pruebas aprobadas en Docker `dev`**, incluidas once nuevas de incorporación:
campos inválidos, rollback total, cambio real de PDF en copia, exclusiones,
perfil, reloj/fin exclusivo, idempotencia y no rehabilitación por replay.
Antes de aplicar se aprobaron 45 pruebas seleccionadas.
Las comprobaciones nuevas también reabrieron los snapshots históricos F2 y
verificaron sus cuatro excluidos/quince pendientes, sin modificar esas pruebas.

[Evidencia nueva](../evidence/lab/20261103/): registros individuales, copias SQLite,
eventos, estado por uso, impacto del índice y dependencias de casos.
Los datos operativos siguen en volúmenes Docker; se exportaron las ramas SQLite
y sus manifiestos, sin snapshots nativos ni copiar un Qdrant abierto.
No se alteraron originales del taller, dependencias, modelos ni entregables previos.
