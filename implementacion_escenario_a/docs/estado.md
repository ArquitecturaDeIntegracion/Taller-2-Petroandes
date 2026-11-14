# Estado de reanudación

Actualizado el 2026-11-13, America/Bogota. Responsable técnico Codex.

## Incremento actual

Se implementó el arnés F9 ampliado autorizado a partir del contraste de las
sesiones 13 y 14. Conserva la recuperación y el descarte del anexo original,
añade fronteras MCP reales y un consumidor sintético con plan fijo, dispatcher
y grader por objetivo. [ADR 0014](adr-0014-arnes-f9-1.md).

Docker dev aprobó 232 pruebas de software. El ensayo integrado aprobó sus
tres fases: F9 original con 19 comprobaciones, MCP real con 17 y consumidor
con 23 casos nuevos, 18 adversariales y cinco benignos. Se observaron 24
propuestas, 18 denegaciones previstas y cinco tareas benignas completadas.
No hubo filtración del canario, contaminación aceptada, errores o inconclusos.

El worker f9-sandbox tiene usuario no privilegiado, raíz y pesos RO, red none,
capacidades vacías y límites de recursos. Solo la carpeta de esta corrida
recibe escritura persistente. La sonda nativa alcanzó un receptor ficticio
antes y después del ensayo; desde el sandbox obtuvo ENETUNREACH al mismo
destino. Se verificaron configuración efectiva, integridad y limpieza propia.
Las 379 fuentes protegidas conservaron su inventario. No se ejecutó la reserva.

[Evidencia actual](../evidence/f9/20261113-arnes-ampliado/README.md) ·
[Guía para validar](validacion-dev-f9-1.md) ·
[Matriz de amenazas y permisos](arnes-f9-1-amenazas.md).

El [resumen ejecutivo Word](../../output/doc/Resumen_Ejecutivo_Arnes_F9_1_PetroAndes.docx)
tiene cuatro páginas revisadas visualmente e incluye un diagrama con iconos
oficiales EIP atribuidos. Es un documento nuevo; conserva los Word anteriores.
Se añadió el [Word de arquitectura y funcionamiento del arnés](../../output/doc/Arquitectura_y_Funcionamiento_del_Nuevo_Arnes_PetroAndes.docx),
con cuatro páginas y dos diagramas revisados visualmente: vista general y
flujo de decisiones. Explica los reportes y distingue MCP real de consumidor
sintético. [Recibo documental](../evidence/f11/20261113-arquitectura-arnes-documento/summary.json).

## Alcance y pendientes reales

Las variantes sintéticas prueban la frontera del consumidor mediante
propuestas forzadas. No acreditan detección semántica ni recuperación RAG
de cada variante. F9 original sí reingiere el corpus y recupera el anexo real.
El cliente LLM y una sesión adversarial completa de Copilot siguen
no_evaluado. No se añadió detector auxiliar ni reanudación durable automática.
Los errores, timeout o interrupción no cuentan como ataques bloqueados.
El aislamiento del worker no limita otras capacidades del IDE del usuario.

La evaluación formal congelada sigue pendiente. Los ocho casos de ajuste y
dieciséis de reserva, sus esperados y decisiones aprobadas no se modificaron
ni se usaron para ajustar el arnés. Laya y el compositor real siguen iguales.

## Presentación y entrega existentes

Se prepararon [consultas directas SQLite y Qdrant para la sustentación](consultas-bases-datos.md).
Docker dev comprobó seis consultas SQL, dos Qdrant y dos rechazos de escritura
o ATTACH. Los 68 IDs coinciden entre las proyecciones; el anexo conserva texto
e identidad y los snapshots no cambiaron. Se usa una copia aislada de revisión
15, sin competir con el MCP activo. [Evidencia](../evidence/db/20261113-sustentacion/summary.json).

La presentación usa una sola conexión petroandes en Inspector y VS Code.
petroandes.demo prepara una copia privada del snapshot aprobado de revisión
15, con 14 documentos y 68 fragmentos y reloj histórico del 8 de noviembre.
El arnés utiliza otros contextos temporales internos; no añade un MCP visible.
[Inspector web](inspector-web.md) · [Copilot y prompts](copilot-vscode.md).

Baseline conserva su diseño de revisión 1 con cuatro excluidos y quince
pendientes. El worker no monta artifacts persistentes ni aplica decisiones.
D01 y D02 mantienen la autorización simulada aprobada y D03 sigue pendiente;
no se concedió acceso adicional por las pruebas nuevas.

F11 conserva su paquete y evidencia anteriores. Este incremento añade su
propia evidencia sin reemplazar la entrega archivada. La evaluación formal
y sustentación del estudiante siguen separadas de la reproducción técnica.
[Entrega técnica](entrega-tecnica.md) · [F11](validacion-dev-f11.md).

El [estado anterior completo](estado-20261113-antes-arnes.md) conserva el
historial de F6 a F11, verificaciones de VS Code, decisiones humanas y los
documentos anteriores. El [historial hasta F5](estado-hasta-f5.md) conserva
las fases iniciales y sus evidencias.
