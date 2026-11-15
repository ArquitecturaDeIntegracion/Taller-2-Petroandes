# Evidencia F9.2: contenido, consumidor MCP y auditoría

Incremento del 14 de noviembre de 2026. Verificación técnica del agente;
no sustituye revisión humana ni ejecuta la reserva formal.

## Resultados comprobados

- [Controlador Docker](docker/summary.json): passed, sin pendientes y limpieza completa.
- [Cuatro fases](docker/ensayo/summary.json): todas aprobadas; reserva sin ejecutar.
- [F9 original](docker/ensayo/f9_original/resultado/summary.json): 19 comprobaciones.
- [MCP real](docker/ensayo/fronteras_mcp/resultado/summary.json): 17 comprobaciones.
- [Flujo PDF nuevo](docker/ensayo/flujo_real_pdf/resultado/summary.json): 12 PDF,
  siete adversariales detectados y cinco benignos sin falsos positivos en este conjunto.
- [Resultados por PDF](docker/ensayo/flujo_real_pdf/resultado/resultados.json):
  recuperación, exposición, señal, resultado, auditoría y chunk objetivo comprobados.
- [Consumidor sintético](docker/ensayo/frontera_consumidor/summary.json): 23/23 casos.
- [Regresión](regresion/command.json): 255 pruebas aprobadas en 189,42 s; una
  advertencia de caché pytest sin escritura en el montaje RO, sin fallos de pruebas.
- [Cliente público restringido](cliente-publico/resultado/summary.json): cuatro
  llamadas completadas sobre petroandes.demo, revisión 15, en f9-sandbox.
- [Inspector actualizado](inspector-servidor/summary.json): respuesta, denegación
  y abstención comprobadas desde su contenedor. [Web HTTP 200](inspector-web.json).
- [Inspección independiente](inspeccion-pdf/resultado/summary.json): el PDF
  original conserva su huella y requiere revisión por cinco señales de contenido.
- [Estructura Docker dev](estructura/command.json): 5.523 archivos textuales,
  sin errores y máximo 199 líneas. [Imagen sin volumen Windows](estructura-imagen/command.json):
  2.706 archivos textuales, sin errores y máximo 199 líneas.
- [Construcción de entrega](build-entrega/command.json) e [identidad de imagen](imagen.json).

La carpeta docker copia íntegramente la corrida
`reports/portable/f9-2-20261114/integrado`. Se verificaron red none, permisos,
recursos, receptor positivo antes/después y 379 fuentes protegidas sin cambios.
El flujo PDF conservó 24 llamadas del cliente y 26 recibos MCP completos;
los PDF originales del ensayo están en `docker/ensayo/flujo_real_pdf/resultado/pdf-sinteticos`.
Los recibos habituales de Inspector se archivaron en `inspector-servidor/auditoria`.
Los del cliente dedicado, en `cliente-publico/auditoria`.

## Intentos y límites conservados

El [intento inicial](intento-inicial/summary.json) del flujo PDF se conserva sin declararlo aprobado:
Inspector devolvía el código 5 esperado para parámetros inválidos y el
verificador esperaba 0. Además, B02 no recuperó su ancla con top_k=5, aunque
el detector no lo marcó como ataque. Se corrigió la aserción y se fijaron diez
candidatos para todos los casos nuevos, conservando RRF y la evidencia inicial.

Las pruebas asíncronas iniciales del host quedaron interrumpidas por la
restricción de sockets de Windows; no se cuentan como una regresión aprobada.
La validación de software y las integraciones efectivas se hicieron en Docker.
Una revisión automática de permisos no pudo iniciar una corrida por límite
temporal de uso; el reintento posterior autorizado sí se ejecutó y está archivado.

Las métricas del flujo PDF y del dispatcher sintético F9.1 se informan por
separado. El consumidor nuevo es un cliente MCP real sin LLM; no acredita
resistencia de Copilot ni detección universal. El documento Word de evaluación
previo se conserva como antecedente, sin sobrescribirlo.
Los índices antiguos deben reingerirse para incluir las señales nuevas.
La demo lo hace en su espacio privado. Los recibos no son un almacén inviolable
ni sustituyen rotación, controles de acceso o monitoreo de un despliegue productivo.
VS Code mantiene su conexión stdio; hay que reiniciar servidores ya abiertos.

`fuentes.jsonl` identifica el código y las guías del incremento. Los archivos
`inventario-*.jsonl` y `integridad.json` permiten verificar esta copia archivada.
El inventario se limita a lectura y huellas; no ejecuta fichas A/R.

[Guía de reproducción](../../../docs/validacion-dev-f9-2.md) ·
[Arquitectura](../../../docs/arnes-f9-2.md) ·
[ADR 0015](../../../docs/adr-0015-arnes-f9-2.md).
