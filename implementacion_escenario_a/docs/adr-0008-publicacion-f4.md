# ADR-0008: publicación local de generaciones E5 y BM25

Fecha: 2026-11-01. Estado: implementado para validación técnica F4.

## Contexto

F3 conserva el inventario completo en staging. Ese inventario no autoriza su
publicación para consulta. F4 necesita un subconjunto gobernado y coherente entre
fragmentos, Qdrant y la rama léxica, incluso cuando no haya certificados.

## Decisión

Se conserva E5 `e5small-es-1.0.0`, sin cambiar motor ni composición extractiva.
El adaptador verifica nueve archivos contra la evidencia F0 y registra versiones
efectivas. El fingerprint incluye esos hashes, prefijos, pooling, normalización,
dimensión y bibliotecas. Un cambio efectivo exige otra generación.
Se compara numéricamente la salida real con media enmascarada y L2.
No se truncan entradas; el input completo debe caber en 448 tokens.

La auditoría de embeddings F3 usa NPY sin pickle, mapa fila/UUID/hash y recibos;
no crea una colección consultable ni concede permisos al corpus pendiente.
Publicación y auditoría son acciones separadas.

Cada perfil tiene un único propietario Qdrant local y una colección nueva por
generación preparada. Se conserva la identidad/hash del PDF en cada payload,
junto con generación, revisión y fingerprint. No se usan snapshots nativos.
Los procesos CLI trabajan por turnos; un futuro servidor deberá poseer la ruta.

La rama léxica `bm25-codes-es-1.0.0` guarda tokens JSON en SQLite y mantiene códigos
con guiones, años y versiones completos. Usa `rank-bm25` sobre el subconjunto
elegible recibido, sin puntuar documentos excluidos. La fusión y los alias de
recuperación pertenecen a F5; no hay cambios a la composición prevista.

Una generación contiene catálogo de fragmentos/padres autorizados, proyección
léxica, manifiesto con hashes y recibo. La proyección densa tiene un hash lógico
de los puntos realmente releídos, ordenados por UUID; no se hashea un directorio
Qdrant abierto. El catálogo publicado conserva gobierno de ingesta como
procedencia y enlaza la revisión actual, sin convertir payloads en permisos.

El registro SQLite de publicaciones cambia el puntero activo en una transacción
después de verificar ambas ramas. La activación toma `BEGIN IMMEDIATE` sobre
gobierno y reevalúa elegibilidad/revisión/período antes de cambiar el puntero.
El lector de snapshots respeta esa transacción externa sin cerrarla.
La apertura activa vuelve a comprobar contexto, revisión, integridad y permisos.
Una revocación o un vencimiento impide reutilizar una generación anterior.

## Consecuencias

Un fallo deja intacto el puntero activo anterior. Puede quedar una colección
preparada sin referencia; se conserva para diagnóstico y no se consulta.
Una generación completa preparada antes del fallo puede verificarse y activarse
en un reintento. Las publicaciones repetidas reutilizan UUID y colección.
No se restauran permisos mediante rollback de índices ni se consumen eventos F2
todavía: propagación y reconciliación del outbox corresponden a F10.

Los perfiles reales pueden tener generaciones activas vacías. Las pruebas
positivas usan documentos, autoridad y decisiones ficticios en directorios
temporales separados; no importan propuestas académicas al gobierno real.

La integridad no sustituye la elegibilidad: F5 deberá derivar IDs desde el registro,
filtrar antes de ambas búsquedas y revalidar antes de devolver resultados.
Este incremento no publica herramientas MCP ni concede autorizaciones operativas.
