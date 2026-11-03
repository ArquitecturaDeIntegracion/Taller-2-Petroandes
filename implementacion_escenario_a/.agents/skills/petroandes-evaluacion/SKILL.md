---
name: petroandes-evaluacion
description: Prepara casos de referencia, calibra laya multilingüe y evalúa anclaje, relevancia, desviación y envenenamiento del Escenario A de PetroAndes. Úsala en F1, F8, F9 y F11 o para revisión independiente de la entrega.
---

# Evaluación de PetroAndes

Lee knowledge/05-calidad.md y la fase aplicable del plan desde tools/read_source.py.
Consulta knowledge/02-gobierno.md para no confundir autoridad con soporte textual.

## Conjunto y arnés

Preparar esperados revisables contra PDF antes de ajustar recuperación.
El plan propone ocho casos de ajuste y dieciséis de reserva; la evaluación final
debe conservar al menos quince casos. Congelar casos, configuración y revisiones.
Registrar por caso perfil, pregunta, hechos y secciones esperadas, prohibidos,
respuesta, citas, rankings, tiempos y resultado del evaluador.

Usar laya multilingüe real con revisión, preguntas y umbral fijados:
noul evalúa proposiciones de soporte y choice pertinencia de fragmentos.
Comprobar longitud del par afirmación/evidencia, sin truncamiento silencioso.
Contrastar juicios con revisión humana; igualdad textual no prueba pertinencia.
Separar anclaje, relevancia, desviación, abstención y validaciones estructurales.
Conservar denominadores, casos no evaluables, fallos y discrepancias del juez.
Sustituir el evaluador requiere ADR, no ocultar una falla de instalación.

## Pruebas críticas

- Recuperar el anexo de COM-PRV-0134, conservándolo y usando filtros normales.
- Mostrar que no cambia políticas ni provoca envío, balances o consejo operativo.
- Probar también una pregunta legítima del documento, sin eliminarlo por completo.
- Documentar capa de contención y límites; reconocer un fallo no es declarar éxito.
- Probar pendientes, revocados, fuera de ámbito y acceso directo a excluidos.
- Probar actualización con vector antiguo presente e idempotencia de eventos.

## Cierre

Verificar Inspector real y reproducción desde PDF con dependencias fijadas.
Separar metas académicas propuestas de resultados y de requisitos del docente.
Si se reutiliza reserva tras corregir, conservar corridas y declarar la reutilización.
No modificar los esperados para favorecer al código ni reportar métricas inventadas.
Actualizar docs/estado.md con hallazgos, evidencia comprobada y pendientes reales.
