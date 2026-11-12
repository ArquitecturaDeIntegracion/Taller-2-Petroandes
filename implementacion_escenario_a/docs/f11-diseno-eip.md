# Correspondencia entre el diseño 3.1 y la implementación

La referencia es el [diseño original 3.1](../../output/doc/Escenario_A_3_1_Analisis_y_Diseno_PetroAndes.docx),
secciones 4 y 5. La correspondencia usa las responsabilidades implementadas
y deja explícitas las simplificaciones del laboratorio.

| Decisión de 3.1 | Implementación y alcance |
| --- | --- |
| ADR 01 · Motor vectorial dedicado | Qdrant local almacena los vectores y SQLite conserva catálogo, gobierno y proyección léxica. El puntero activo se cambia tras verificar las proyecciones. El almacenamiento local tiene un solo propietario por vez. [F4](adr-0008-publicacion-f4.md) · [F10](f10-operacion.md). |
| ADR 02 · Partición estructural con contexto | `structural-es-1.0.0` preserva secciones, páginas, cabeceras y relación padre/hijo. El límite es 448 tokens E5. Una sección íntegra y breve puede quedar por debajo del tamaño objetivo. [F3](adr-0007-extraccion-estructural.md). |
| ADR 03 · Composición determinista | F6 selecciona extractos y filas con citas y revalida gobierno antes de devolverlos. Se abstiene ante insuficiencia, conflicto o ámbito ambiguo. El anexo marcado se conserva para auditoría y se descarta al componer. [F6](adr-0010-composicion-f6.md) · [F9](validacion-dev-f9.md). |
| ADR 04 · Bundle versionado | E5 se verifica por revisión y hash, con prefijos, pooling con máscara, normalización L2 y 384 dimensiones. F10 reconstruye y compara una colección con el mismo bundle, reutiliza entradas idénticas en propagación y somete la reversión a gobierno vigente. Un cambio real de bundle o partición requiere su contrato y casos revisados. [F4](f4-indices.md) · [F10](validacion-dev-f10.md). |

| Etapa implementada | Patrón EIP de 3.1 | Correspondencia práctica |
| --- | --- | --- |
| Recepción | Channel Adapter, Message Endpoint | Los comandos F2, F3 y F10 leen archivos y registran eventos locales. El operador inicia la carga. |
| Extracción | Message Translator, Canonical Data Model | El parser traduce PDF a contratos con tablas, secciones y procedencia. |
| Gobierno documental | Content Enricher | El registro aporta hash aprobado, ámbito, uso, grupos y fechas de efectividad. |
| Extracción inválida | Invalid Message Channel | F3 conserva el informe de cuarentena e impide activar una ingesta incompleta. |
| Partición | Splitter | Fragmentos y padres conservan IDs, orden y páginas. |
| Organización | Pipes and Filters | Catálogo, ingesta, publicación, recuperación y composición tienen contratos y etapas separadas. |
| Propagación | Event Message, Idempotent Receiver | El outbox SQLite se consume bajo demanda. Los reintentos convergen a la revisión vigente y el replay confirmado queda sin efecto. |
| Elegibilidad | Message Filter | Ambas ramas y la obtención directa consultan la misma política antes de devolver evidencia. |
| Recuperación híbrida | Scatter-Gather, Aggregator | El servicio combina rankings de Qdrant y BM25 con prioridad por código exacto. Las ramas se ejecutan por turnos en el proceso local. |
| Evidencia de consulta | Content Enricher | La selección añade fragmentos autorizados y expande contexto dentro de la misma política. |
| Salida | Content Filter, Message Translator | F6 escoge unidades citables. MCP expone salida estructurada con esquema y errores. |
| Trazabilidad | Correlation Identifier, Message History | IDs de correlación, eventos, hashes y revisiones enlazan el documento, la proyección y la respuesta. |
| Evaluación | Wire Tap, Message Store | Los arneses guardan entradas, candidatos, respuestas y juicios. La captura se realiza al ejecutar las pruebas. |

La analogía EIP describe el flujo de datos. La exactitud de una tabla depende
del parser y de su contraste. La vigencia depende del registro de gobierno.
La pertinencia requiere evaluación y la contención del anexo requiere sus
controles de acceso y composición. La propagación se ejecuta bajo demanda,
por lo que las mediciones del laboratorio no acreditan vigilancia continua.
