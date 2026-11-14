# Evidencia del arnés F9 ampliado

Corrida del 13 de noviembre de 2026, America/Bogota. Verificación técnica
del agente; no constituye una nueva aprobación humana documental.

## Resultados

- [Resultado integrado](docker/ensayo/summary.json): tres fases y fuentes intactas.
- [Controlador Docker](docker/summary.json): passed, pending vacío y limpieza completa.
- [Tres fases](docker/ensayo/summary.json): passed e inventario protegido intacto.
- [F9 original](docker/ensayo/f9_original/resultado/summary.json): 19 comprobaciones.
- [Fronteras MCP reales](docker/ensayo/fronteras_mcp/resultado/summary.json): 17 comprobaciones y 14 llamadas tools/call.
- [Consumidor sintético](docker/ensayo/frontera_consumidor/summary.json): 23 casos, 18 adversariales y cinco benignos.
- [Regresión](regresion/command.json): salida 0, 232 pruebas en 212,45 segundos.
- La construcción del código está en build-final; build-entrega añade el Word final a la imagen.
- [Estructura Docker dev](estructura/command.json), [Windows](estructura-host/command.json) e [imagen de entrega](estructura-paquete/command.json): sin errores y máximo 199 líneas por archivo.

El ensayo de las tres fases tardó 778,21 segundos en este equipo.
Los recibos guardan cada comando, stdout y stderr en partes de 160 líneas.
La carpeta docker es copia íntegra de reports/portable/f9-guard-20261113-01.

## Cómo interpretar la evidencia

La F9 original recupera el anexo real bajo permisos académicos explícitos,
lo descarta en composición y permite su lectura íntegra como dato de auditoría.
Las variantes nuevas se entregan a un cliente determinista con propuestas
forzadas, sin LLM. Sus 24 propuestas produjeron 18 denegaciones previstas,
cinco lecturas autorizadas del doble y un borrador benigno verificado.
No hubo efectos externos, filtración, contaminación aceptada o inconclusos.
Los benignos miden utilidad del dispatcher sintético, no del compositor F6.

El mismo receptor TCP ficticio respondió a los controles nativos antes y
después. El sandbox devolvió ENETUNREACH; no se aceptó timeout ni conexión
rehusada como prueba de defensa. Inspect y proc verificaron UID10001,
NoNewPrivs, capacidades, montajes mínimos y límites de recursos.
Solo esta corrida fue RW. No se montaron artifacts persistentes ni Docker.sock.

379 archivos protegidos conservaron el mismo inventario. No se ejecutó
reserva A/R ni se modificaron permisos, corpus o conexiones del cliente.
Las huellas de los archivos archivados quedan en inventario-*.jsonl.
El código y documento emitidos quedan identificados en fuentes.jsonl.

El LLM real sigue no_evaluado. La regla F6 de anexos permanece limitada;
este ensayo no prueba detección universal ni seguridad de todo Copilot.
La guía distingue resultados comprobados de esperados al repetir.

[Guía de reproducción](../../../docs/validacion-dev-f9-1.md) ·
[Diseño](../../../docs/adr-0014-arnes-f9-1.md).
