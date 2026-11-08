# ADR-0010 · Composición extractiva gobernada

Fecha 2026-11-07. Versión de reglas `extractiva-es-1.0.0`.

La salida de F5 ordena candidatos por relevancia de recuperación. F6 necesita
demostrar que cada extracto trata la consulta y conserva sus condiciones.
La CLI ofrece `responder` y reutiliza el contrato `SearchResponse` de F1.
El compositor es una función interna de la consulta de F5. Consume el ranking
y las partes publicadas autorizadas del mismo snapshot. La revalidación de
gobierno ocurre después de componer. Si cambian revisión o elegibilidad,
se descartan los extractos y los IDs de la traza.

## Unidades y procedencia

Una afirmación es un pasaje literal o una cabecera con su fila original.
Para un tramo se conserva la definición direccional de la anomalía con el
umbral y la ventana. La fila de una ficha requiere el tag del activo y la
presión de descarga. Para MAOP se exige la distinción literal entre diseño
y alarma. La salida omite las filas de otros tramos o parámetros.

`evidencia` contiene vistas extractivas de los fragmentos citados. Conservan
el ID del fragmento publicado, identidad y hash del PDF, ubicación y marcas
de origen. Su campo `texto` contiene solo el extracto devuelto. La obtención
gobernada de F5 permite consultar el fragmento completo.

Para secuencias, se exige el objeto del procedimiento y el contexto de
prerrequisitos o abortos enlazado por F3. Para una recomendación o un anuncio
de firmware, se exigen sus secciones de alcance o condiciones de aplicación.
Cada sección debe tener todas las partes del padre publicado, en orden.
Los párrafos de condiciones y las excepciones se citan desde su propio
fragmento. Se conserva la negación y la estructura de las filas.

## Reglas de suficiencia

La regla combina intención explícita, familia documental, uso del servicio,
código y versión cuando aparecen, y título de la sección. Se admiten estas
familias de consulta técnica.

| Intención | Ancla y uso específico |
| --- | --- |
| Alarma de presión por tramo | Criterios de detección de procedimiento, instrucción operativa |
| MAOP por tramo | Parámetros de diseño de manual, límite de diseño |
| Presión de descarga de activo | Datos de operación de ficha, especificación de activo |
| Incertidumbre de medición | Artículo de resolución, referencia normativa |
| Tolerancia de conciliación | Criterios de aceptación de procedimiento, instrucción operativa |
| Secuencia por código | Secuencia de procedimiento, instrucción operativa |
| Recomendación y firmware por código | Comunicación de proveedor, recomendación |
| Decisión de acta por código | Decisiones de acta, evidencia histórica |

La lectura histórica permite extraer la familia correspondiente cuando
el catálogo autoriza ese uso, y se rotula como lectura histórica. Las familias
documentales conservan su función. Un acta o comunicación queda fuera de la
selección para instrucción operativa. Los filtros y la consulta estrechan el
ámbito y el código, incluso cuando el índice contiene otros documentos.
La falta de tramo, los ámbitos contradictorios, la ausencia de un ancla
completa y varias unidades competitivas producen abstención. Las consultas
de cálculo, comparación, telemetría y cifras oficiales siguen rutas de
abstención. La plantilla rotula el uso y muestra `sin versión` para una cita
con valor nulo.

Los anexos y los fragmentos marcados por F3 como instrucciones dirigidas
al procesador quedan fuera de afirmaciones y evidencia de F6. La traza de
auditoría registra los IDs de candidatos descartados por esa causa. Su texto
permanece accesible mediante obtención directa cuando la política lo permite.
El ensayo de ataque de extremo a extremo corresponde a F9.

## Verificación y ajuste

Se usan comprobaciones técnicas ad hoc con el corpus y permisos simulados en
una copia histórica, más controles aislados de cambios de gobierno. Las
reglas son conservadoras. La calibración con los ocho casos de ajuste y
la evaluación final requieren esperados revisados. Los casos académicos
conservan sus fichas separadas. [Estado de reanudación](estado.md).
