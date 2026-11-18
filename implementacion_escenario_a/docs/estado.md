# Estado de reanudación

Actualizado el 2026-11-16, America/Bogota. Responsable técnico Codex.

## Entrega documental actual

Se creó el [Word de arquitectura C4 niveles 1 y 2](../../output/doc/PetroAndes_C4_Contexto_y_Contenedores.docx)
con dos páginas horizontales y una vista por página. El contexto presenta al
consultante, los clientes MCP y PetroAndes; los contenedores separan la aplicación
Python del catálogo, las proyecciones de consulta y los recibos de auditoría.
Usa nombres funcionales para el cliente y conserva los entregables anteriores.
Se exportó con Microsoft Word y se inspeccionaron las dos páginas rasterizadas
con render_docx.py. [Recibo documental](../evidence/f11/20261116-c4-contexto-contenedores-word/summary.json).
Este incremento no cambió código de aplicación ni ejecutó Docker, ataques o reserva.

Se conservan el [C4 de componentes](../../output/diagrams/PetroAndes_C4_Componentes_Servicio_Consulta_Cliente_20261116.png)
y la [vista dinámica de consulta](../../output/diagrams/PetroAndes_C4_Flujo_Consulta_Cliente_20261116.png),
con sus SVG y recibos enlazados en el historial. Son vistas del mismo servicio.

## Estado técnico vigente

El incremento F9.2 permanece implementado: señales de texto y de propiedades
visuales del PDF, control en composición, recibos por llamada MCP y cliente de
prueba con plan fijo. El arnés completo se ejecuta bajo demanda y sus reportes
no alimentan automáticamente la consulta. [Diseño](arnes-f9-2.md) · [ADR](adr-0015-arnes-f9-2.md).

La validación Docker dev del 14 de noviembre aprobó 255 pruebas de regresión,
el corpus original, las fronteras MCP, doce PDF nuevos y 23 casos sintéticos.
Se mantiene la distinción entre detección, descarte y exposición literal autorizada.
[Evidencia técnica](../evidence/f9/20261114-arnes-contenido/README.md) · [Guía](validacion-dev-f9-2.md).

Inspector y VS Code usan la conexión lógica única petroandes. La demostración
prepara una copia privada por proceso del snapshot aprobado de revisión 15,
con reloj histórico del 8 de noviembre, 14 documentos y 68 fragmentos publicados.
Qdrant funciona embebido y la conexión MCP usa stdio.
[Inspector](inspector-web.md) · [Copilot](copilot-vscode.md).

Las decisiones aprobadas, el corpus original y baseline se conservan. D01 y D02
mantienen sus condiciones simuladas de laboratorio; D03 continúa pendiente.
La clasificación revisada del original conserva 14 certificados, 4 excluidos
y 1 pendiente. Los originales y las evidencias previas siguen archivados.

La evaluación formal congelada y una sesión adversarial completa de Copilot
siguen pendientes; no se usaron los casos de reserva para ajustar el sistema.
Próximo paso: sustentación con la guía y los diagramas, manteniendo explícito
el contexto histórico de la demostración. [Entrega técnica](entrega-tecnica.md).

## Historial conservado

El [estado anterior completo](estado-20261116-antes-word-c4-niveles-1-2.md)
conserva el detalle de F9.2, consultas a bases, documentos anteriores, la propuesta
actualizada y la modificación del original aprobada por el estudiante. Sus enlaces
remiten a los historiales previos, decisiones humanas y evidencia de F0 a F11.
