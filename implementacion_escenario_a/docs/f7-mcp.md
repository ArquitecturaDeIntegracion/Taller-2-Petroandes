# F7 · Servidor MCP de consulta documental

El servidor `PetroAndes` ofrece dos herramientas de lectura por stdio.
Usa el SDK Python `mcp==1.30.0` fijado en el lock. La versión de los contratos
anunciada por el servidor es `0.1.0`.
[SDK Python fijado](https://github.com/modelcontextprotocol/python-sdk/tree/v1.30.0).

## Contratos publicados en tools/list

| Herramienta | Entrada | Salida estructurada |
| --- | --- | --- |
| `buscar_documentos` | `consulta` de 1 a 2000 caracteres, `top_k` entero entre 1 y 10 con valor inicial 5, `filtros` opcional con `tipo`, `activo` y `tramo` | `SearchResponse` con estado, afirmaciones citadas, evidencia, revisión, generación y correlación |
| `obtener_fragmento` | `doc_id`, `version_documental` explícita de tipo cadena o `null`, `section_id`, `parte` entera positiva y `pdf_sha256` opcionales | `FragmentResponse` con estado, partes ordenadas, citas, revisión, generación y correlación |

Los esquemas de entrada y salida se generan a partir de los contratos F1.
El catálogo de herramientas se anuncia con indicaciones de solo lectura.
El primer bloque de texto contiene el mismo JSON que `structuredContent`.
En búsqueda, un segundo bloque presenta los extractos con el uso documental
y las citas legibles. La obtención marca el texto como contenido no confiable.
[Modelos y esquemas F1](contratos.md).

### Estados y errores

| Categoría | Resultado |
| --- | --- |
| Esquema de herramienta inválido | `isError: true` con `parametros_invalidos`, sin eco del valor recibido |
| Nombre de herramienta desconocido | `isError: true` con `herramienta_desconocida` |
| Abstención de búsqueda | `estado: abstencion`, motivo explícito y listas de evidencia y afirmaciones vacías |
| Denegación de obtención | `estado: denegado`, `evidencia_no_autorizada`, partes y citas vacías |
| Referencia ambigua | `estado: error`, `referencia_ambigua` cuando la referencia requiere una huella |
| Proyección inválida o ausente | `estado: error`, `indice_no_listo` |
| Despliegue no disponible | `estado: error`, `servicio_no_disponible` sin divulgar rutas ni excepciones internas |

Los estados de dominio están en el contrato estructurado de salida. Los
errores de protocolo se gestionan en el SDK. Las abstenciones conservan los
motivos de F6. El catálogo actual conserva una huella activa por código y
versión. El selector de ambigüedad se prueba con dos referencias de ensayo.
[Especificación de herramientas MCP](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).

## Ejecución y alcance

El proceso recibe el perfil al arrancar y toma el contexto de
`config/f4-context.json`. Los argumentos MCP se validan con los modelos de
consulta. Cada operación abre el catálogo en lectura y reutiliza F5 o F6.
E5 se carga localmente y se reutiliza dentro de la sesión. Las operaciones
de Qdrant se ejecutan por turnos y liberan el almacenamiento al terminar.

El transporte escribe JSON-RPC UTF-8 en un descriptor reservado. Los demás
mensajes del proceso, incluidas las escrituras nativas en stdout, se redirigen
a stderr. La sonda del canal comprueba negociación, llamada y cierre limpio.

Las llamadas positivas se reproducen en una copia histórica de laboratorio
con decisiones ya registradas y un reloj de prueba. El despliegue habitual
usa el reloj del servicio. Con sus permisos actuales, una búsqueda se
abstiene y una referencia directa se deniega. El ensayo conserva el
catálogo temporal separado del volumen de uso habitual.

[Guía de validación](validacion-dev-hasta-f7.md) ·
[Inspector oficial](https://modelcontextprotocol.io/docs/tools/inspector).
