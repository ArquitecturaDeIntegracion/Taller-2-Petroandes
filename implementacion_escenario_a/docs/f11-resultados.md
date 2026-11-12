# Resultados y pendientes de la entrega técnica

El alcance es la parte práctica del Escenario A. Los perfiles de gobierno
se mantienen separados. Baseline tiene cuatro exclusiones documentadas,
quince documentos pendientes y cero certificaciones. El laboratorio
histórico usa doce decisiones simuladas registradas, con identidad de
prueba, ámbito y fecha controlados. El laboratorio persistido llegó después a
la revisión 15 con 14 certificaciones simuladas y MAN-OPE-004 v2 pendiente.
[Registro de aplicación](../evidence/revision/20261108-confirmada/registro/summary.json).

| Área | Evidencia y resultado de referencia |
| --- | --- |
| PDF, SQLite, E5 y Qdrant | La ingesta obtiene 92 fragmentos de 19 PDF. El contexto histórico publica 58 puntos de doce documentos elegibles. El baseline se abstiene y deniega el acceso a la versión excluida de PRO-MED-007. |
| MCP | Inspector verifica dos herramientas, esquemas, errores, paridad con Python y reapertura del índice. [Guía F7](validacion-dev-hasta-f7.md). |
| Evaluación diagnóstica | F8 observó respaldo en 2 de 2 afirmaciones, pertinencia en 3 de 9 candidatos, Recall@5 medio de 1,0 en 2 búsquedas respondidas y desviación en 0 de 4 casos. Los 6 candidatos restantes se conservaron como no pertinentes. El umbral de respaldo 0,5 es diagnóstico. [Resultados F8](../evidence/f8/20261108/summary.json). |
| Ataque | F9 recupera el anexo de COM-PRV-0134 y F6 lo descarta. La auditoría autorizada conserva el texto marcado. La consulta legítima sigue recuperando firmware 7.4. El ensayo cubre el servicio y su composición. [Resultados F9](../evidence/f9/20261108/summary.json). |
| Cambios de gobierno | La prueba F10 conserva un vector revocado mientras se deniega la lectura, confirma eventos tras activar el índice y verifica reintentos, reindexación con el bundle vigente y reversión. [Resultados F10](../evidence/f10/20261108/final/summary.json). |

Las observaciones de F10 fueron 229 ms de p95 en cinco consultas calientes,
8 ms para una revocación durante consulta y 2,52 s para una reaprobación.
Los objetivos de diseño son 3 s, 60 s y 15 minutos, respectivamente.
La muestra es del laboratorio y excluye el tiempo humano de certificación.
El operador inicia la propagación bajo demanda. La migración a otro
bundle o partición tiene su propio requisito de evaluación.

## Revisión académica confirmada

El grupo aprobó ocho casos de ajuste y dieciséis de reserva. Las fichas
versionadas incluyen las decisiones, fuentes y contextos aprobados.
Docker verificó las huellas y preparó un catálogo independiente por caso.
La ejecución formal está pendiente. Corresponde publicar los índices de
prueba, calibrar con ajuste y evaluar al menos quince casos de reserva con
sus denominadores y discrepancias. Los cuatro casos F8 corresponden a una
prueba diagnóstica independiente. [Matriz congelada](revision/20261108-confirmada/matriz.md).

La [guía de validación](validacion-dev-f11.md) incluye el ejercicio de
sustentación que debe completar el estudiante. La [matriz de diseño](f11-diseno-eip.md)
explica el alcance de los cuatro ADR y las simplificaciones de los EIP.
[Evidencia de la ejecución F11](../evidence/f11/20261108/README.md).

## Archivos de entrega y licencias

Conserva la relación entre las bases `app` y `project` que registra el
manifiesto `entrega/archivos-*.jsonl`. Incluye código, configuración,
dependencias fijadas, los PDF originales, documentos del taller y evidencias
históricas. Incluye los catálogos SQLite de prueba necesarios para reproducir
los ensayos. Adjunta la carpeta de resultados F11. Deja fuera entornos
virtuales, pesos, cachés, índices de trabajo y salidas temporales.

`entrega/licencias-*.jsonl` conserva la versión, licencia declarada o
archivo de licencia presente en cada distribución Python o paquete npm
instalado en la imagen. La ausencia de metadata se registra para revisión,
incluido el paquete local del taller. Docker instala Inspector mediante
`npm ci` a partir del [lock npm](../config/inspector-npm-lock.zip).
Los pesos se obtienen de sus revisiones
fijadas. Sus fichas declaran MIT para E5 y Apache-2.0 para laya.
[Ficha E5](https://huggingface.co/intfloat/multilingual-e5-small/tree/fd1525a9fd15316a2d503bf26ab031a61d056e98) ·
[Ficha laya](https://huggingface.co/convaiinnovations/laya-multilingual/tree/e4e9ddf21a7b1903b7acffd8814ad4307bf63a67).
