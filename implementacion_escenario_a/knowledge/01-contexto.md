# Contexto curado de la asignatura y de PetroAndes

## Alcance y orden de consulta

- Este conocimiento orienta decisiones; no sustituye los documentos fuente ni afirma que la aplicación exista.
- Trabajo autorizado para una ejecución futura: únicamente la práctica 3.2 del Escenario A, consulta documental gobernada.
- El agente de Codex ayuda a desarrollar y revisar; el servicio entregado tendrá flujo fijo, sin agente, bucle de razonamiento ni orquestación.
- El Escenario B, acceso a OT, envíos regulatorios reales, interfaz gráfica y despliegue productivo quedan fuera de esta ruta.
- El [enunciado](<../../Contenido de la Actividad.docx>) determina los mínimos; el [diseño 3.1](<../../output/doc/Escenario_A_3_1_Analisis_y_Diseno_PetroAndes.docx>) fija las decisiones acordadas.
- El [plan de la Alternativa 1](../../plan_trabajo_alternativa_1_escenario_a.md) concreta fases, interfaces y evidencias. Sus casillas no son resultados ejecutados.
- Cambiar motor, composición, embeddings o evaluador exige documentar el ADR y sus consecuencias antes de alterar el comportamiento.

## Principios del curso que cambian el diseño

1. La integración es una capacidad de negocio: motivador → escenario de calidad → capacidad → decisión → KPI con línea base.
2. Blueprint explica qué integrar y por qué; footprint concreta tecnologías y operación. No confundir una elección de producto con una justificación arquitectónica.
3. Un escenario de calidad declara fuente, estímulo, artefacto, ambiente, respuesta y medida. Los objetivos de latencia son propuestas hasta medirlos.
4. Interoperar requiere significado, unidades, reglas e identidad compartidos, además de un formato común.
5. La propiedad del dato determina autoridad y dirección del intercambio. El índice es una proyección, no la fuente de verdad de vigencia.
6. Consolidación carga una copia persistente; propagación mantiene destinos al cambiar el origen. Aplican a carga inicial y mantenimiento del corpus.
7. La cercanía vectorial no certifica actualidad, permiso, fuerza documental ni corrección de una cifra.
8. Todo atributo usado para filtrar necesita metadatos desde la ingesta; el prefiltro actúa antes o junto con cada búsqueda.
9. Reintentos necesitan identidad e idempotencia. Reconstruir un índice no debe restaurar autorizaciones revocadas.
10. Los EIP describen responsabilidades, pero Translator, Enricher o Aggregator no garantizan verdad, autoridad ni comprensión semántica.

Fuente ampliada: [contexto de la asignatura](../../contexto_arquitectura_integracion.md), secciones 4, 5, 9, 11 y 15.

## PetroAndes en el nivel necesario para esta práctica

- PetroAndes y las cifras del caso son ficticias y pedagógicas; no son evidencia operativa ni regulación real.
- Empresa energética integrada: upstream, AndesTransporte en midstream, dos refinerías, comercialización y gestión HSE/transición.
- Creció con sistemas aislados. Planillas, archivos y correos producen conciliaciones manuales, reportes repetidos y BI con días o semanas de rezago.
- Los cinco procesos son contratos/regalías; nominación/balance; refinación/suministro; comercial/FEPC; y HSE/emisiones.
- La consulta documental resuelve un dolor transversal: localizar la versión aplicable de manuales, procedimientos, normas, actas y comunicaciones.
- Más de 350 sistemas y 400.000 tags caracterizan la complejidad del caso, no la carga de este prototipo de 19 documentos.
- La estrategia contempla nube corporativa, lakehouse, contratos de datos, OSDU y APIs/eventos; no se asumen ya desplegados.
- Purdue/ISA-95 organizan la referencia industrial; DMZ nivel 3.5 separa OT e IT; IEC 62443 se cita para zonas y conductos.
- El caso prohíbe escritura directa corporativa/nube sobre control. El enunciado del taller es más restrictivo: ningún componente accede directamente a OT.
- Esta práctica no necesita SCADA, historiadores, SAP, correo ni datos reales de balance: solo el corpus y sus decisiones de gobierno.
- No trasladar umbrales o SLO de ejemplos de clase al caso como si fueran requisitos del PDF.

Fuentes: [contexto PetroAndes](../../ARTI4212_Caso_PetroAndes.md), secciones 1, 5, 6 y 7; [caso original](../../ARTI4212_Caso_PetroAndes.pdf), páginas 3, 6 y 7.

## Corpus y respuesta esperada

- Son 19 documentos lógicos con representaciones PDF y Markdown, no 38 fuentes independientes.
- Procesar los [PDF originales](../../corpus/pdf/); los [Markdown](../../corpus/md/) sirven para contrastar extracción y depurar, sin sustituir ingesta.
- Las seis familias son manuales, procedimientos, resoluciones ficticias, actas, comunicaciones y fichas de activos.
- No hay estado de vigencia declarado: se deriva evidencia de sustitución y se registra una decisión de la autoridad, nunca una etiqueta inventada por el modelo.
- Separar identidad, versión, sección, páginas, hash, ámbito, autoridad y uso autorizado. Véase [gobierno del corpus](02-gobierno.md).
- La respuesta cita documento, versión y sección en cada afirmación y conserva cifras, unidades, negaciones y condiciones.
- Composición extractiva no equivale a corrección: una cita auténtica de otra columna, equipo o ámbito sigue siendo un fallo.
- Ante fuente no autorizada, ambigüedad, conflicto, evidencia insuficiente o pregunta fuera del corpus, abstenerse explícitamente.
- No usar conocimiento general del asistente para completar límites operativos ni calcular una cifra oficial de balance.

Fuente de reglas del corpus: [LEEME](../../corpus/LEEME.md).

## Decisiones acordadas de la Alternativa 1

| Responsabilidad | Elección que se conserva |
| --- | --- |
| Entorno | Laboratorio local en Python; SQLite para catálogo y decisiones |
| Vector | qdrant-client local persistente; un único proceso propietario de su almacenamiento |
| Extracción | PDF con pypdf; otra extracción solo ante fallo demostrado y trazable |
| Semántica | intfloat/multilingual-e5-small; revisión fd1525a9fd15316a2d503bf26ab031a61d056e98 |
| Bundle | e5small-es-1.0.0; 384 dimensiones, prefijos query:/passage:, promedio con máscara, L2 y coseno |
| Partición | structural-es-1.0.0; estructura documental antes que cortes ciegos |
| Límites | Objetivo 250–350 tokens, máximo 448 en entrada completa de embedding; solape de prosa hasta 40 dentro de sección |
| Léxico | Códigos completos y BM25 solo sobre elegibles; fusión RRF registrada |
| Respuesta | Pasajes y tablas con plantilla determinista y citas; sin modelo generativo |
| Interfaz | SDK MCP Python, transporte stdio y MCP Inspector real |
| Evaluación | laya multilingüe: noul para soporte y choice para pertinencia; calibración y revisión humana |

Las versiones de bibliotecas y hashes efectivos se fijarán al comprobar compatibilidad; no se fabrican ahora. Consultas y documentos usan el mismo bundle.
Una tabla dividida repite cabecera, unidades y ámbito; nunca corta filas. Secuencias conservan condiciones, orden y vínculo al padre.
El índice léxico y el vectorial comparten manifiesto. Obtener un fragmento por ID no elude la política de búsqueda.
No abrir la misma ruta Qdrant local desde servidor MCP y evaluación simultáneamente: usar turnos o consultar al proceso propietario.

## Mínimos de cumplimiento que no pueden simplificarse

- Ingesta y procedencia comprobables sobre los 19 PDF; originales intactos.
- Gobierno con autoridad, evidencia y perfiles separados; incertidumbre del corpus conservada.
- Recuperación semántica y léxica con prefiltro común, también en expansión de contexto y acceso directo.
- Dos herramientas MCP completas: buscar_documentos y obtener_fragmento por documento, versión y sección; Inspector real.
- Al menos 15 casos con esperado revisado y arnés que reporte anclaje, relevancia y desviación con denominadores.
- Las abstenciones y no evaluables se reportan aparte; no reciben calidad perfecta automáticamente.
- Conservar y recuperar el anexo envenenado; probar qué capa contiene el ataque o documentar un fallo real.
- Consolidación, cambios de gobierno, revocación y reconstrucción reproducibles; no basta con generar código.
- Un mock no sustituye modelos, Qdrant o Inspector reales; un evaluador alternativo exige ADR.
- El plan propone objetivos de actualización p95 ≤15 min, revocación ≤60 s y consulta caliente p95 ≤3 s: no son garantías observadas ni mínimos de nota docente.
- No inventar aprobaciones, esperados, hashes, métricas, comandos ejecutados ni capturas.

Para secuencia y evidencias detalladas, consultar el [plan](../../plan_trabajo_alternativa_1_escenario_a.md), F0–F11 y R01–R10.
