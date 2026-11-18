# Estado de reanudación

Actualizado el 2026-11-16, America/Bogota. Responsable técnico Codex.

## Incremento actual: F9.2 validado

Se añadió el [C4 de componentes del servicio](../../output/diagrams/PetroAndes_C4_Componentes_Servicio_Consulta_Cliente_20261116.png)
y su [SVG editable](../../output/diagrams/PetroAndes_C4_Componentes_Servicio_Consulta_Cliente_20261116.svg), con nombres funcionales para el cliente.
[Recibo de componentes](../evidence/f11/20261116-c4-componentes-servicio/summary.json): SVG, PNG y legibilidad; sin nuevas pruebas Docker, ataques ni reserva.
Se conserva la [vista dinámica C4](../../output/diagrams/PetroAndes_C4_Flujo_Consulta_Cliente_20261116.png)
con su [SVG](../../output/diagrams/PetroAndes_C4_Flujo_Consulta_Cliente_20261116.svg) y [recibo](../evidence/f11/20261116-diagrama-consulta-cliente/summary.json), además de las versiones previas.

Se implementó la mejora autorizada del informe: detector de contenido y
propiedades visuales del PDF, auditoría por llamada MCP con cierre ante fallo
de escritura y cliente MCP real con plan fijo, sin LLM ni intérprete de acciones.
Se añadieron doce PDF nuevos a través de ingesta, E5, Qdrant, composición,
MCP e Inspector. Se mantienen la conexión única, corpus, permisos y reserva.
[ADR 0015](adr-0015-arnes-f9-2.md) · [Arquitectura](arnes-f9-2.md).

Docker dev aprobó 255 pruebas de regresión y las cuatro fases integradas:
F9 original (19 comprobaciones), fronteras MCP (17), flujo de doce PDF nuevos
(7 adversariales detectados, 5 benignos sin falsos positivos) y los 23 casos
sintéticos F9.1. El flujo nuevo produjo 24 llamadas del cliente y 26 recibos
completos; comprobó recuperación, exposición literal y descarte del chunk objetivo.
Se verificó aislamiento SO con receptor positivo antes/después, limpieza propia
y conservación del inventario de 379 fuentes protegidas. No se ejecutó reserva.

El cliente dedicado completó las cuatro consultas de presentación con revisión
15. Inspector web fue recreado, respondió HTTP 200 y sus pruebas MCP reales
de respuesta, denegación y abstención pasaron en el contenedor actualizado.
La configuración VS Code sigue válida; un proceso anterior debe reiniciarse
desde MCP: List Servers. No se declara una nueva sesión humana de Copilot.

Se conserva el intento inicial inconcluso: aserción de código Inspector
incorrecta y control B02 fuera del top 5. La batería nueva usa top_k=10 sin
cambiar RRF. Los PDF, recibos, resultados y comandos quedan archivados.
La estructura pasó en Docker dev (5.523 archivos, máximo 199 líneas) y en la
imagen construida. El inventario de entrega conserva las huellas de fuentes
y evidencias. Próximo paso: usar la guía para la sustentación; un ensayo
adversarial de Copilot o la evaluación formal requerirían alcance explícito.
[Guía F9.2](validacion-dev-f9-2.md) ·
[Evidencia del incremento](../evidence/f9/20261114-arnes-contenido/README.md).

Se añadió el [Word de funcionamiento F9.2 con C4 y EIP](../../output/doc/Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx).
Sus cuatro páginas incluyen C4 de contenedores y componentes, flujo EIP con
iconos atribuidos, algoritmo, auditoría, consulta de ejemplo, evidencia y límites.
Se verificó con Microsoft Word y cuatro imágenes de página inspeccionadas.
La emisión documental no volvió a ejecutar pruebas de ataque ni reserva.
[Recibo documental](../evidence/f11/20261114-documento-f9-2/summary.json).

Se añadió el [Word actualizado de arquitectura completa C4 y EIP](../../output/doc/Arquitectura_Actual_PetroAndes_C4_EIP_F9_2.docx).
Sus cuatro páginas explican contexto, aplicaciones, almacenes, componentes,
ingesta, gobierno, búsqueda híbrida, MCP, F9.2, cambios F10 y evaluación F8.
Incluye tres diagramas C4 y uno EIP con iconos atribuidos, revisados en Word.
Se contrastaron 23 archivos de implementación con la evidencia conservada;
no se repitieron ataques ni reserva y se conservaron los documentos anteriores.
[Recibo documental](../evidence/f11/20261114-arquitectura-actual-c4-eip/summary.json).

Se añadió el [Word del diagrama integral EIP](../../output/doc/Diagrama_Integral_EIP_PetroAndes_Actual.docx),
en dos páginas A3 horizontales. Incluye 41 elementos en cinco carriles y una
matriz de 21 filas con patrones, controles y rutas de implementación; conserva
ingesta, gobierno, ambas herramientas MCP, F10, auditoría, F8, F9.2 y F11.
Se verificaron paginación, lectura visual, referencias y correspondencia de IDs.
[Recibo documental](../evidence/f11/20261114-diagrama-integral-eip/summary.json).

Se añadió el [Word EIP con el estilo visual solicitado](../../output/doc/Arquitectura_EIP_Servicios_MCP_y_Arnes_PetroAndes.docx),
en dos páginas A3 horizontales. El plano usa iconos abiertos y bandas como
la imagen de referencia, explicita buscar_documentos y obtener_fragmento e
incorpora auditoría obligatoria y arnés F9.2. La segunda página explica rutas,
parámetros, funcionamiento y límites. Se revisaron las dos páginas en Word.
[Recibo documental](../evidence/f11/20261114-eip-referencia-servicios-arnes/summary.json).

Se añadió el [Word de despliegue y flujo completo con iconos tecnológicos](../../output/doc/Despliegue_PetroAndes_Flujo_Completo_Tecnologias.docx),
en dos páginas A3 horizontales. Distingue Windows, Docker, contenedor dev de
VS Code, Inspector con hijo Python, volúmenes, temporales por proceso,
ingesta, publicación y consulta MCP. Incluye F9.2 y evaluación laya fuera
de la consulta. Se verificaron 13 iconos, configuración y dos páginas renderizadas.
[Recibo documental](../evidence/f11/20261114-despliegue-tecnologias/summary.json).

Se regeneró la [guía Word de pruebas](../../output/doc/Guia_Actualizada_Pruebas_PetroAndes_F9_2.docx)
en cinco páginas, conservando la anterior. Incluye Docker dev, Inspector,
nueve casos MCP con JSON, cuatro prompts Copilot, lectura del anexo, auditoría
y ejecución integral F9.2. Sus parámetros coinciden con config/demo-pruebas.json.
Se revisaron las cinco páginas renderizadas; no se repitieron ataques ni reserva.
[Recibo documental](../evidence/f11/20261114-guia-pruebas-f9-2/summary.json).

Se consolidó la [arquitectura final en Word](../../output/doc/Arquitectura_Final_PetroAndes_C4_EIP_F9_2.docx)
en seis páginas con C4 de contexto, contenedores y componentes, despliegue,
EIP integral y arquitectura F9.2. Distingue MCP lógico, procesos, perfiles,
persistencia y ensayos. Se conservaron documentos previos y evidencia Docker.
Las seis páginas se revisaron en Word; no se ejecutaron ataques ni reserva.
[Recibo documental](../evidence/f11/20261115-arquitectura-final/summary.json).

Se actualizó la [propuesta 3.1 en Word](../../output/doc/Escenario_A_3_1_Analisis_y_Diseno_PetroAndes_Actualizado_20261115.docx),
partiendo del archivo de la raíz y conservando original, formato y cuatro ADR.
La revisión de 18 páginas actualiza matriz por perfil, metadatos, MCP, F10,
seguridad F9.2, EIP y resultados diagnósticos; distingue objetivos y pendientes.
Se contrastaron código y evidencias previas; no se ejecutaron ataques ni reserva.
[Recibo documental](../evidence/f11/20261115-propuesta-3-1-actualizada/summary.json).

Por aprobación expresa del usuario se editó el [original de la raíz](../../Escenario_A_3_1_Analisis_y_Diseno_PetroAndes.docx)
con un solo estado por documento: 14 certificados, 4 excluidos y 1 pendiente.
Se actualizaron fundamentos, resumen y conclusión; D01/D02 conservan sus
condiciones y D03 sigue pendiente. [Respaldo previo](../../output/doc/versiones/20261115-antes-clasificacion-aprobada/Escenario_A_3_1_Analisis_y_Diseno_PetroAndes.docx).
Se revisaron sus 14 páginas; los catálogos y paquetes archivados no se editaron.
[Recibo de la modificación autorizada](../evidence/f11/20261115-clasificacion-original-aprobada/summary.json).

Se añadió el [Word del flujo de consulta y equivalentes C4](../../output/doc/Flujo_Actual_Consulta_PetroAndes_y_Vistas_C4.docx),
con cuatro páginas y diagramas funcional, contexto, contenedores y componentes.
Aclara dos rankings RRF, apoyo de códigos, revalidación y cierre de auditoría;
el cambio de gobierno no produce reintento automático dentro de la llamada.
[Recibo documental](../evidence/f11/20261115-flujo-consulta-c4/summary.json).

## Revisión documental previa del arnés

Se añadió el [informe Word de evaluación frente a la clase 14](../../output/doc/Informe_Evaluacion_Arnes_Clase14_PetroAndes.docx),
con cuatro páginas y dos diagramas revisados visualmente. Concluye alineación
parcial: distingue el filtro estructural F6, las pruebas reales del servidor y
el consumidor sintético. Propone contener y observar el consumidor real,
ampliar la detección y validar el flujo desplegado. Ese informe no aplicaba las
mejoras; F9.2 las implementa ahora sin sobrescribir el documento de evaluación.
Se contrastó evidencia Docker anterior y los hashes de 19 archivos técnicos;
no hubo una nueva corrida Docker ni ejecución de reserva.
[Recibo de revisión](../evidence/f9/20261114-evaluacion-clase14-README.md).

## Antecedente validado: F9.1

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

## Alcance del antecedente F9.1 y pendientes

Las variantes sintéticas prueban la frontera del consumidor mediante
propuestas forzadas. No acreditan detección semántica ni recuperación RAG
de cada variante. F9 original sí reingiere el corpus y recupera el anexo real.
El cliente LLM y una sesión adversarial completa de Copilot siguen
no_evaluado. F9.2 incorpora el detector y recibos; no añade reanudación durable automática.
Los errores, timeout o interrupción no cuentan como ataques bloqueados.
El aislamiento del worker no limita otras capacidades del IDE del usuario.

La evaluación formal congelada sigue pendiente. Los ocho casos de ajuste y
dieciséis de reserva, sus esperados y decisiones aprobadas no se modificaron
ni se usaron para ajustar el arnés. Laya sigue igual; F9.2 versiona el filtro del compositor.

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
