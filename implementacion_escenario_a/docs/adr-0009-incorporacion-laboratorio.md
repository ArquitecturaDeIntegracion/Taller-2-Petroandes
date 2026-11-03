# ADR-0009: incorporación administrativa de certificaciones simuladas

Fecha: 2026-11-03. Estado: aplicado al lote autorizado por Jonnathan Caballero.

## Contexto y autoridad

El usuario autorizó doce decisiones individuales para laboratorio, con ámbito
`general:corpus_revision`, grupo `LAB_REVISION` y usos limitados por documento.
La autorización es una instrucción de esta conversación, conservada con SHA-256;
no es una firma digital ni prueba de identidad o autoridad empresarial real.
Las propuestas del 1 de noviembre no se convierten automáticamente en decisiones.

## Decisión

La entrada administrativa vive fuera de MCP y no acepta perfil baseline.
`ApprovalRequest` y doce fichas conservan selección, versión nullable, roles
simulados, usos, restricciones, revisor, ámbito, grupo, fin y evidencia del usuario.
Se rechazan campos extra, vacíos, placeholders, duplicados y períodos inválidos.
No se admite un inicio efectivo proporcionado en el archivo de entrada.

Antes de escribir se comprueban todas las identidades, exclusiones y hashes de
los PDF reales contra el registro. Se construyen todos los `DecisionRecord`
validados antes de la primera inserción. Las resoluciones asumen publicación
y aplicabilidad únicamente en el intervalo académico; no registran una fecha
histórica de publicación ni se contrastan con leyes reales de Internet.

`register` captura el reloj real America/Bogota dentro de la transacción, después
de validar los PDF. Esa hora identifica el registro de la revisión recibida;
no se inventa una hora de envío del mensaje. `effective_from == revisado_en`.
El fin es `2026-12-01T00:00:00-05:00`, exclusivo, sin intervalo abierto.

La autenticidad `verificada` pertenece explícitamente al supuesto académico;
la autoridad se rotula `SIMULACIÓN ACADÉMICA: rol de ...` en cada decisión.
El supuesto individual vincula el rol competente, revisor y restricciones.
El índice y el texto documental no acreditan autoridad real ni permisos operativos.

Una transacción exterior `BEGIN IMMEDIATE` engloba las doce decisiones. El
almacén respeta transacciones externas, como ya lo hace el lector de snapshots.
Cada decisión sigue creando su revisión y evento propio; un fallo intermedio
revierte todo el lote. La revisión esperada impide aplicar sobre un estado cambiado.

Los IDs derivan de la solicitud normalizada y del hash/identidad del PDF. Repetir
el lote reconoce sus decisiones originales y conserva hora/revisión; nunca
reaplica una autorización antigua por encima de una revocación posterior.
Un lote histórico parcial o distinto se rechaza y no se completa silenciosamente.

## Proyecciones y eventos

La publicación usa el contexto confiable ya configurado del servicio. Ese contexto
no coincide con el ámbito/grupo autorizado; su conjunto elegible permanece vacío.
Se prepara una generación vacía de revisión 13 y se verifica/activa con F4;
no se cambia la configuración para forzar una consulta positiva.
La política sí verifica los doce permisos en el contexto educativo autorizado,
sin convertir ese contexto de prueba en configuración del servicio ni parámetro MCP.

Los trece eventos permanecen en el outbox con su historial. Se conserva un recibo
de reconciliación del contexto actual, sin marcarlos globalmente entregados:
no hay un consumidor de todos los contextos, sondeo ni proceso F10 completo.
Cambiar legítimamente el contexto requerirá configuración administrativa explícita
y una nueva publicación coherente. No se afirma propagación automática ni SLO.

## Evidencia y límites

Copias SQLite antes/después, decisiones, eventos, permisos por uso, período y
huellas de baseline/índices/casos acompañan al lote. Las pruebas conservan las
validaciones históricas y añaden controles sobre copias aisladas y el estado nuevo.
No cambian motor, bundle, compositor ni evaluador. No se aprueban casos de
referencia, no se ejecuta el anexo y no hay acciones operativas ni envíos externos.
