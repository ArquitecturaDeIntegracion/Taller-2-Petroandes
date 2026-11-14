# Consultas de bases para sustentación

Corrida técnica del 13 de noviembre de 2026, America/Bogota.
[Resumen](summary.json) · [Guía](../../../docs/consultas-bases-datos.md).

Docker dev aprobó seis SELECT reales, dos consultas Qdrant y dos rechazos SQL
(DELETE y ATTACH). El catálogo de revisión 15 conserva 19 documentos,
14 decisiones y 15 eventos. La publicación tiene 68 fragmentos de 14
documentos y vectores de 384 dimensiones con distancia coseno.

Los 68 IDs coinciden en catálogo de fragmentos, proyección léxica y Qdrant.
El anexo COM-PRV-0134 tiene el mismo texto e identificador en SQL y Qdrant,
contenido_no_confiable verdadero y marcas de seguridad en la proyección SQL.
El snapshot original y la copia de gobierno conservaron el mismo SHA-256.

La consulta densa P-101 presión de diseño devolvió la ficha FIC-ACT-P101,
secciones 2, 4 y 3, con puntajes aproximados 0,8949, 0,8623 y 0,8579.
Es un ranking observado, sin BM25 ni composición o autorización MCP.

Cada carpeta conserva SQL ejecutado o argumentos, salida, errores y recibo.
Las denegaciones esperadas tienen exit_code 1; el resumen integrado es passed.
datos-manifest.json identifica la copia usada y las rutas relativas dentro
de reports/portable/db-sustentacion-20261113-validacion/datos.
Las bases derivadas permanecen allí; no se duplican en este archivo de evidencia.

No se abrió el índice privado del MCP ni se modificaron decisiones, corpus
o fichas A/R. La copia usa reloj histórico del 8 de noviembre y no declara
vigencia operativa. Consultar una base directamente es inspección del operador;
no demuestra por sí solo la contención del documento envenenado.
