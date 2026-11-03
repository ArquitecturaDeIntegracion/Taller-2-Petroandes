# ADR-0007: extracción PDF con disposición y staging verificable

Fecha: 2026-11-01. Estado: decisión técnica implementada en F3.
No certifica documentos ni supone revisión académica de esperados.

## Contexto observado

La extracción plana de pypdf devuelve celdas separadas. La disposición del PDF
conserva columnas, pero incluye filas y cabeceras multilínea. Las primeras pruebas
detectaron una cabecera partida, celdas numéricas de un carácter y un considerando
regulatorio omitido. La revisión visual detectó además dos encabezados nominales
del boletín COM-PRV-0098 que debían reconocerse como secciones independientes.

## Decisión

- Mantener pypdf 6.21.4 como extractor; usar `extraction_mode="layout"`.
- Implementar parser `pypdf-layout-es-1.0.1`. La versión 1.0.0 fue intermedia;
  sus corridas se conservan y no se usan como salida final de F3.
- Reconstruir tablas con posiciones de columnas, separadores físicos de filas y
  trazas por página/línea. Las continuaciones se unen en su propia celda.
- Rechazar alineación ambigua, filas incompletas, cuerpo ausente o diferencias
  de contraste. No rellenar celdas ni completar contenido desde Markdown.
- Contrastar encabezados, palabras, cifras, signos y unidades contra Markdown.
  El contraste verifica la extracción; nunca construye secciones o fragmentos.
- Mantener `structural-es-1.0.0`, objetivo 250–350 y máximo real de entrada E5 448.
  Las secciones breves se conservan completas: no se mezclan artículos o ámbitos
  para aumentar su tamaño. El solape adicional de prosa elegido es cero (máximo 40).
- Si se excede 448, dividir entre párrafos o filas completas y repetir cabeceras y
  condiciones comunes. Una unidad indivisible excedida va a revisión, sin truncar.
- Repetir como contexto trazable prerrequisitos/principios y aborto de secuencias,
  y condiciones/alcance de recomendaciones. Conservar las secciones fuente.
- Derivar UUID de ubicación, PDF, versiones técnicas e input completo. Cambiar
  contexto o contenido del embedding cambia la identidad; perfil/gobierno no autorizan
  por sí mismos el texto. Los perfiles se almacenan en generaciones separadas.
- Preparar una generación SQLite íntegra en temporal y renombrarla al completarla.
  No activar índice vectorial/léxico ni cambiar el registro de gobierno desde F3.

## Alternativas consideradas

Reemplazar PDF por Markdown eliminaría la evidencia de extracción exigida.
Concatenar celdas de la extracción plana ocultaría mezclas de columnas. Una librería
alternativa no resultó necesaria para estos 19 PDF, al verificar disposición, filas
y contraste. No se introdujo un servicio externo ni un modelo generativo.

## Consecuencias y límites

Se conserva texto PDF, tablas normalizadas, fuente por líneas, contexto común,
gobierno con null explícito, relaciones, input exacto de embedding y huellas.
El bundle E5, su revisión, pooling y normalización de 3.1 no cambian; F3 usa su
tokenizador real offline. `config/embedding-bundle.json` registra huellas observadas
en F0, comprobadas de nuevo contra los archivos usados en Docker.

Los 19 PDF son de una página. No se afirma cobertura universal de PDF multipágina,
escaneados o tablas arbitrarias. La validación detecta defectos y exige revisión.
La inspección visual es técnica del agente, no certificación del estudiante.
La composición y el evaluador permanecen sin cambios; no se evaluó aún recuperación.
Una preparación con rechazos no cumple la puerta de salida de F3 para F4.
