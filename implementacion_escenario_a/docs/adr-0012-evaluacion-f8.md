# ADR-0012 · Evaluación diagnóstica de F8

Fecha 2026-11-08. Estado adoptado para la prueba técnica.

F8 reutiliza el checkpoint multilingüe de laya fijado en F0. `noul` mide
respaldo por afirmación con los fragmentos originales citados. `choice`
registra pertinencia para los primeros cinco candidatos fusionados de cada
búsqueda. El umbral `0,5` es diagnóstico y se registra sin calibración. Antes
de inferir, se verifica el límite de 1024 tokens con la construcción de entrada
del evaluador. Un par demasiado largo queda como no evaluable.

Las citas, el hash, la versión, la sección, las páginas y las líneas literales
se contrastan con fragmentos elegibles del ensayo. Recall@5 cuenta secciones
esperadas recuperadas en casos respondidos. Las abstenciones se reportan por
separado. Los juicios de laya, las comprobaciones de procedencia y la paridad
Python/MCP conservan sus resultados individuales.

La captura con E5 e Inspector se ejecuta en un proceso que finaliza antes de
cargar laya. Así se liberan los modelos de recuperación y los hijos stdio
antes de evaluar. Se conserva la decisión de usar un único propietario por
vez para el índice local.

La suite de cuatro controles documentados permite verificar la integración.
Para calibrar y evaluar la reserva se requieren casos revisados y sus
contextos materializados. [Reproducción](validacion-dev-f8.md) ·
[Evidencia diagnóstica](../evidence/f8/20261108/).
