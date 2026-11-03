# Contratos MCP de la consulta documental

## Herramientas mínimas

`buscar_documentos` recibe consulta no vacía, top-k entre 1 y 10 y filtros
opcionales de tipo, activo o tramo. Devuelve estado, respuesta extractiva o
abstención, evidencia ordenada, citas, revisiones y correlation_id.

`obtener_fragmento` recibe doc_id, version_documental como cadena o null y
section_id; puede usar parte o hash para desambiguar. Devuelve texto o partes
ordenadas, citas, procedencia y marcas de confianza bajo la misma autorización.
Una emisión sin versión no se convierte en v1 ni se resuelve por fecha más reciente.

Definir por herramienta nombre, descripción destinada al modelo, parámetros
JSON Schema, esquema de retorno, errores y ejemplos positivos y negativos.
No permitir autoasignarse grupos, perfil de gobierno, estado ni prioridad.
La identidad de laboratorio se configura en el servicio, fuera de la consulta.

## Adaptador

Usar el SDK oficial Python en una versión fijada y compatible con sus ejemplos.
MCP adapta el servicio probado; no duplica ni debilita sus controles.
Mantener stdout exclusivamente para protocolo y enviar logs a stderr o archivo.
Comprobar que descargas, librerías y carga de modelos no impriman en stdout.
Usar rutas absolutas y argumentos separados al configurar el cliente.

Separar errores de esquema/protocolo de errores de dominio:
evidencia no autorizada, referencia ambigua, índice no listo e indisponibilidad.
No revelar material restringido mediante mensajes de error o diagnósticos públicos.
Si el catálogo o la revisión no se pueden confirmar, no ampliar la consulta.

## Verificación real

En MCP Inspector comprobar inicio, negociación, tools/list y tools/call.
Guardar versión, comando exacto y salidas de ambas herramientas:
una llamada válida, abstención, referencia denegada y parámetros inválidos.
Comparar con el mismo caso ejecutado por la función Python.
Cerrar y reabrir el proceso para verificar liberación y persistencia del almacén.
Una prueba directa o un cliente simulado no sustituye Inspector.

El fragmento no confiable puede inspeccionarse como datos etiquetados para
auditoría. El compositor no lo presenta como instrucción operativa. No se
habilitan herramientas de correo, modificación de políticas o acceso a balances.
La seguridad de un cliente LLM externo no queda demostrada por el servidor.

## Referencias

- [SDK oficial Python](https://github.com/modelcontextprotocol/python-sdk).
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector).
- Contratos detallados: fase F7 del plan registrado como `plan` en sources.json.
