# Arquitectura de la Alternativa 1

## Dependencias que se deben comprobar

Python, Pydantic, pypdf, SQLite, qdrant-client, Sentence Transformers,
PyTorch, rank-bm25, SDK MCP Python, pytest y laya multilingüe.
F0 verifica compatibilidad y fija versiones; un paquete instalado no demuestra
que su modelo, transporte o almacenamiento funcionen. Node se usa para Inspector.

## Representación y fragmentos

- Ingesta desde los 19 PDF; Markdown se usa solo para contraste.
- Conservar sección, páginas, hash del PDF, versión o emisión y relaciones.
- Partición `structural-es-1.0.0`: objetivo 250–350 tokens, máximo 448 contando
  título, contexto y prefijo efectivamente enviados al modelo.
- Dividir por sección/artículo; conservar condiciones, unidades y cabeceras.
- Solape de prosa hasta 40 tokens dentro de una sección. No cortar filas.
- Conservar bloque padre y orden para reconstruir secuencias autorizadas.
- Una extracción dudosa se revisa y no se publica como evidencia válida.

## Bundle de embeddings fijado en 3.1

- Modelo `intfloat/multilingual-e5-small`.
- Revisión `fd1525a9fd15316a2d503bf26ab031a61d056e98`.
- Bundle `e5small-es-1.0.0`, dimensión 384, coseno.
- Prefijos `query:` y `passage:` también para español.
- Pooling promedio con máscara y normalización L2; validar el adaptador real.
- Registrar revisión de tokenizador, versiones y hashes calculados.
- No mezclar bundles aunque coincidan las dimensiones; evitar truncamiento.

## Almacenes y consulta

SQLite conserva documentos, fragmentos, decisiones, relaciones y revisiones.
Qdrant local guarda la proyección densa; el catálogo gobierna la elegibilidad.
Primero resolver autorizaciones por metadatos y luego enviar IDs elegibles
y revisión como filtro de la consulta densa. Si no hay elegibles, abstenerse.
BM25 puntúa solo los fragmentos elegibles; complementar con códigos completos.
Conservar guiones, años, versiones y alias declarados; fusionar posiciones con RRF.
La expansión de contexto y `obtener_fragmento` reutilizan la misma política.
Revalidar gobierno antes de devolver; una carrera causa reintento acotado o abstención.

## Persistencia y actualizaciones

Qdrant local requiere un único propietario del almacenamiento. No abrir la ruta
simultáneamente desde CLI, servidor y evaluador. Alternar procesos o usar el
servidor MCP como propietario; una necesidad real de concurrencia justifica
evaluar un servidor Qdrant local. No usar snapshots nativos en modo local.

Consolidación es la carga inicial; propagación distribuye decisiones y cambios.
Un archivo cambiado queda pendiente: no hereda aprobación de un hash anterior.
Eventos y decisiones se registran juntos; consumidor idempotente y revisión común.
Publicar generaciones completas mediante manifiesto; nunca activar una parcial.
Una revocación afecta la elegibilidad aunque el vector siga físicamente presente.
Reindexar en colección nueva al cambiar bundle o partición; comparar y activar
coordinadamente. El rollback técnico no restaura autorizaciones revocadas.

## Módulos previstos

`schemas`, `catalog`, `governance`, `extract`, `chunk`, `embeddings`,
`vector_store`, `lexical`, `retrieve`, `compose`, `mcp_server`, `evaluate`,
`update` y `cli`. Crear solo lo necesario para la fase activa del plan.
No existe todavía una CLI `petroandes` por haber creado este agente.
