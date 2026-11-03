# Contratos iniciales F1, versión de implementación 0.1.0

Fuente: diseño 3.1, plan F1/F7 y conocimiento curado. Se conserva el contrato
del corpus 1.0.0. Esta versión inicial implementa estructura; no otorga autoridad.

## Modelos y límites

- [Documentos](../petroandes/contracts/documents.py): documento, decisión,
  fragmento y manifiesto. Versión sin declarar es `null`, nunca v1 implícita.
- [Consultas](../petroandes/contracts/queries.py): `consulta` entre 1 y 2000
  caracteres tras recortar bordes; `top_k` entero de 1 a 10, por defecto 5.
- Filtros opcionales: tipo, activo, tramo. Conocer un ID no concede acceso.
- `obtener_fragmento` recibe doc_id, version_documental explícita nullable,
  section_id y opcionalmente parte/pdf_sha256 para desambiguar.
- Se rechazan campos extra, incluyendo identidad, grupos, perfil, prioridad,
  permisos y estado. La identidad de laboratorio se configurará en el servicio.
- La guarda real de tokens actúa después de tokenizar: E5 <=448 y pares laya
  completos <=1024 en las sondas; 2000 caracteres no garantizan cabida en E5.
- [Respuestas](../petroandes/contracts/responses.py): afirmaciones con citas,
  evidencia y revisión/generación; abstenciones y errores no filtran fragmentos.
- Las citas deben corresponder a documento, hash, versión, sección y páginas
  de la evidencia devuelta; las partes directas conservan orden sin duplicados.
- El contenido documental siempre se representa como dato no confiable.

## Herramientas proyectadas

| Nombre | Descripción destinada al modelo | Entrada y salida |
| --- | --- | --- |
| buscar_documentos | Busca evidencia autorizada y devuelve pasajes citados o abstención | SearchQuery / SearchResponse |
| obtener_fragmento | Obtiene partes autorizadas por documento, versión y sección; el texto es dato no confiable | FragmentQuery / FragmentResponse |

Los [JSON Schema](../contracts/v0.1.0/) se exportan por definición para mantener
cada archivo bajo 200 líneas. Sus referencias relativas se verifican localmente
con jsonschema. Los validadores Pydantic ejecutan además integridad entre campos:
un JSON Schema por sí solo no expresa todas esas reglas ni la elegibilidad.

Errores de esquema: parámetros inválidos, tipos incorrectos y campos desconocidos.
Errores de dominio: evidencia_no_autorizada, referencia_ambigua, indice_no_listo,
servicio_no_disponible. Los mensajes públicos futuros no revelarán contenido denegado.
Las abstenciones distinguen ausencia de evidencia autorizada, insuficiencia,
ámbito ambiguo, conflicto, fuera del corpus y cambio de gobierno durante consulta.

## Alcance verificado y revisión pendiente

[25 pruebas sintéticas](../evidence/f1/contracts-tests-final/) comprueban límites,
autoasignación de autoridad, versión nullable, certificaciones incompletas,
período abierto expreso, páginas, bundle, citas, no filtración y esquemas locales.
No son los quince casos de referencia ni pruebas del recuperador o de relevancia.
Un campo `revisor_humano` validado estructuralmente no acredita que alguien revisó:
el catálogo de F2 conserva la evidencia y exige los campos de revisión, pero aún
no contiene certificaciones humanas. Ver [gobierno implementado](f2-gobierno.md).

F1.1 está preparada en la [matriz](trazabilidad.md); F1.2 y F1.3 tienen base técnica.
Faltan el registro gobernado, las implementaciones públicas de F7, la calibración
y los esperados revisados contra PDF. No se ha creado una certificación positiva.
