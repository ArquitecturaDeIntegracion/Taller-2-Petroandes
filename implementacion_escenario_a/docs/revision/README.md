# Guía de revisión: decisiones documentales y casos de referencia

Preparado: 2026-11-01. Estado: **propuesta pendiente de revisión humana**.
Este paquete no registra tu aprobación, no concede permisos y no modifica catálogos.

## Por dónde empezar

1. Revisa la [matriz de los 19 documentos](matriz-documental.md).
2. Abre la ficha JSON de cada fila para consultar hash, fuentes, supuesto y pregunta.
3. Revisa la [matriz de los 24 casos](matriz-casos.md) y sus vistas detalladas.
4. Registra tu decisión individual, las correcciones y tu nombre/fecha reales.

Las matrices son la vista de lectura; los JSON conservan los detalles para futuras
consultas. No son registros `DecisionRecord` ni un archivo de autorizaciones importable.
El [manifiesto del paquete](manifest.json) enumera las 19 fichas y los 24 casos.

## Qué es evidencia, supuesto y decisión

| Capa | Qué contiene | Qué no demuestra |
| --- | --- | --- |
| Evidencia del corpus | PDF, SHA-256, página, sección y texto declarado | No certifica por sí sola vigencia ni autenticidad |
| Supuesto de laboratorio | Rol emisor simulado, ventana, ámbito, uso y grupo propuestos | No es una aprobación real del área ni del profesor |
| Decisión pendiente | Tu aceptación, corrección, rechazo o solicitud de información | No está tomada por el agente ni por este paquete |

Los 19 PDF se leyeron como fuentes; Markdown no sustituyó esa lectura. Los IDs de
sección corresponden a F3. En exclusiones, la evidencia puede estar en el documento
sucesor; cada ficha identifica también el hash del documento al que se refiere.

## Decisiones que debes revisar por documento

- Comprueba identidad, versión y emisor. Un valor null significa «sin versión».
- Abre la página y sección indicadas; contrasta valores, tablas y condiciones.
- Distingue estado del baseline de la propuesta para el perfil de laboratorio.
- Decide si aceptas el supuesto específico del rol emisor representado por el grupo.
- Revisa el uso, ámbito exacto, grupo y período propuestos. Puedes restringirlos más.
- Confirma si la evidencia es suficiente o si debes conservar el documento pendiente.

El resultado actual sigue siendo cuatro excluidos y quince pendientes. Se propone
conservar esas cuatro exclusiones, mantener MAN-OPE-004 v2 pendiente y considerar
14 candidaturas individualmente. No es una solicitud para aprobarlas en bloque.
MAN-OPE-004 no se identifica como el manual retirado: esa identidad sigue desconocida.
Los otros manuales también requieren un supuesto explícito; no están exentos de la duda.

### Alcance inicial propuesto

Las candidaturas permiten solo **lectura descriptiva** del contenido en laboratorio,
con uso `evidencia_historica`, ámbito `general:corpus_revision` y grupo `LAB_REVISION`.
No equivalen a habilitar instrucciones operativas, límites actuales ni normas reales.
Para probar otros usos habrá que preparar y revisar decisiones específicas adicionales.
D18 añade una autorización propuesta de `inspeccion_no_confiable` para leer el anexo.
Su contenido seguirá siendo dato no confiable; nunca se autoriza ejecutar sus órdenes.

La ventana sintética propuesta es `[2026-11-01 00:00, 2026-12-01 00:00)`, zona -05:00.
Es una condición de los fixtures, no una fecha de publicación extraída del PDF.
En las resoluciones ficticias, emisión no acredita publicación. Para el laboratorio
se debe aceptar o corregir explícitamente ese supuesto; no investigar leyes reales.
En una materialización futura, conserva tu fecha real de revisión. Si queda fuera
de la ventana elegida, versiona fechas/fixtures; no inventes una revisión retroactiva.

## Qué debes revisar en los casos

- [A01–A08: ajuste](casos-ajuste.md), para desarrollar y ajustar la recuperación.
- [R01–R08: reserva](casos-reserva-1.md) y [R09–R16: reserva](casos-reserva-2.md).
- Comprueba pregunta, esperado semántico, cifras/unidades, versión y citas.
- Revisa si corresponde responder, abstenerse o denegar acceso directo.
- Acepta o corrige identidad/grupos/ámbito/uso y las precondiciones sintéticas.
- Verifica qué documentos deben seguir excluidos o pendientes.

Cada caso usa una **copia aislada** inicial de catálogo y generación. Solo se
materializan las propuestas requeridas por ese caso, después de tu revisión.
No hereda aprobaciones ni revocaciones de otro caso. Baseline no recibe decisiones
positivas; laboratorio persistido tampoco se modifica al preparar este paquete.
Todas las decisiones del fixture deben respetar hash, revisión de gobierno, período,
autenticidad, autoridad y revisión humana. No basta con escribir «certificado».
La fecha controlada pertenece al reloj interno de pruebas, nunca a parámetros MCP.

R09/R10/R11/R12 incluyen revocación, cambio de hash, vencimiento y conflicto sintéticos;
no son hechos observados en los PDF. La prueba de vector revocado requiere un índice
real y las rutas finales de recuperación/acceso: permanece propuesta para fases futuras.
A01 no devuelve cifras aunque el texto exista. R05/R14 deben abstenerse sin evidencia
ni afirmaciones de salida, como exige el contrato actual. Sus fuentes justifican la
revisión del esperado y no son permisos para mostrar pasajes al usuario.

### Reserva y métricas

La división propuesta es 8 de ajuste y 16 reservados; conserva al menos 15 finales.
Los dieciséis no deben usarse para optimizar. Tu lectura para revisar los esperados
es parte de la preparación; cualquier uso posterior para ajustar debe declararse.
Después de tus correcciones, versionar y congelar casos/fixtures con sus hashes.
Actualmente no están congelados ni ejecutados; no hay resultados de métricas.
Recall de respuesta se calcula solo en casos respondibles y con el denominador visible.
Abstenciones, denegaciones y contención del ataque se evalúan por separado.
No contar una respuesta vacía como anclaje perfecto ni cambiar el esperado para pasar.

## Cómo devolver tu revisión

Puedes responder por ID o completar una copia versionada de las fichas. Usa:

| Campo | Qué debes indicar |
| --- | --- |
| ID | D01–D19 o A01–A08/R01–R16 |
| Decisión | Documento: aceptar propuesta limitada, corregir, mantener pendiente o rechazar |
| Decisión de caso | Validar esperado, corregir o sustituir; justificar cambios |
| Correcciones | Texto, evidencia, ámbito, uso, grupos o período que deseas cambiar |
| Revisor | Tu nombre o integrante del grupo que realizó la revisión |
| Fecha | Fecha real de la revisión, con zona horaria si se registra hora |
| Justificación | Página/sección y supuesto aceptado o información que falta |

En los archivos entregados esos campos permanecen pendientes o null. La mera creación
de estas fichas no acredita tu lectura. Puedes revisar por lotes pequeños y conservar
sin decisión lo que no hayas examinado. Ningún caso debe marcarse aprobado por omisión.

## Qué ocurrirá después

Tras tu revisión se preparará una versión revisada de los casos y, si autorizas la
aplicación de decisiones concretas, su incorporación controlada solo a laboratorio.
La CLI administrativa actual ofrece inicialización y estado; no se implementó aquí
un importador ni se ejecutaron escrituras de gobierno. No cargar estos JSON como
certificaciones ni modificar SQLite manualmente para eliminar el pendiente.
El desarrollo técnico independiente de F4 puede continuar mientras revisas.

Esta revisión del grupo es parte del diseño educativo del proyecto. El enunciado
pide declarar regla y fuente de autoridad; no establece aquí un trámite de firma
formal del profesor. Las 24 propuestas son una elección del plan, no 24 casos exigidos
por el docente. La entrega requiere al menos quince casos de referencia.
