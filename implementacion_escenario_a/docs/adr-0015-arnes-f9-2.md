# ADR 0015 Contenido no confiable, auditoría y consumidor MCP real

Fecha: 2026-11-14. Implementación autorizada por Jonnathan Caballero.
Referencia: informe `Informe_Evaluacion_Arnes_Clase14_PetroAndes.docx`.
Este incremento F9.2 complementa el [ADR 0014](adr-0014-arnes-f9-1.md).

## Problema

F9.1 separaba correctamente recuperación, gobierno y ejecución, pero F6
marcaba anexos por su nombre. Sus variantes del consumidor eran sintéticas;
no recorrían la ingesta y el MCP real. Una consulta cotidiana tampoco dejaba
un recibo persistente por llamada. El IDE conservaba capacidades ajenas al MCP.

## Decisiones

1. Sustituir la marca por prefijo `anexo-` por señales del contenido y del PDF.
   El detector `contenido-no-confiable-1.0.0` normaliza Unicode, examina órdenes
   de cambio de instrucciones, rol, ocultación y envío externo. Decodifica
   variantes acotadas base64/URL exclusivamente para inspección. No las ejecuta.
2. Revisar el PDF con trazas de pintado y píxeles renderizados por PyMuPDF:
   texto invisible, fuera de página, microscópico o sin contraste y páginas
   sin texto verificable. Las señales visuales afectan conservadoramente a
   todos los fragmentos de esa página. No hay OCR ni comparación semántica.
3. Conservar PDF, texto original e identidad. Las señales excluyen unidades
   de la composición; no cambian la autorización documental. La obtención
   directa autorizada sigue entregando texto literal no confiable para auditoría.
4. Versionar staging con el detector. Los índices con metadatos antiguos se
   consideran pendientes de revisión de seguridad al componer. Deben reingerirse.
   La demostración prepara automáticamente una generación privada nueva.
5. Cambiar el compositor a `extractiva-es-1.1.0` por el nuevo filtro, conservando
   las reglas de suficiencia, E5, BM25, RRF, contratos de respuesta y permisos.
6. Registrar cada `tools/call` recibido, incluidos rechazos de esquema, antes
   de devolver evidencia. El recibo empieza como `iniciado` y se reemplaza
   atómicamente por `completado` tras flush/fsync. Si no puede escribirse, la
   llamada falla con `auditoria_no_disponible` y no entrega contenido documental.
7. Incorporar un consumidor real MCP dedicado, sin LLM: valida un plan completo
   de hasta diez lecturas, lo congela antes de abrir la sesión y verifica
   contrato, coherencia de representaciones y literalidad de cada afirmación.
   No interpreta acciones de los documentos ni acepta servidores desde ellos.
   La CLI fija `petroandes.demo`. La ejecución recomendada usa `f9-sandbox`.
8. Añadir doce PDF nuevos de laboratorio: siete adversariales y cinco benignos.
   Recorren parser PDF, contraste, E5, SQLite, Qdrant, F6, MCP real, cliente e
   Inspector. Se conserva aparte la batería sintética de 23 casos de F9.1.

## Trazabilidad y seguridad

Los recibos incluyen correlation_id, huellas de entrada/salida, contexto de
autorización, revisión, generación, decisiones, señales e identidades de
fragmentos. No guardan consulta, texto documental ni credenciales. Los hashes
permiten correlacionar; no son anonimización fuerte ni firma contra manipulación.
`capa` indica el control observado; un descarte de un candidato ajeno no prueba
que causara la abstención. El ensayo comprueba además el chunk objetivo exacto.
Los recibos son archivos locales del laboratorio, sin rotación ni almacén WORM.
Un proceso interrumpido puede dejar un recibo `iniciado`, nunca contado como éxito.

La política de acceso sigue dependiendo del catálogo, hash, ámbito, uso y
tiempo; ninguna señal del texto concede acceso. Se conservan baseline, D01/D02,
D03 pendiente y los ocho casos de ajuste y dieciséis de reserva sin ejecutarlos.

PyMuPDF 2.1 y sus dependencias quedan fijados en `requirements-portable.lock`.
Solo se emplean APIs locales de inspección/renderizado; no se añade un LLM,
descarga de modelos del detector ni un servicio externo.
Fuentes: [trazas de PyMuPDF](https://pymupdf.readthedocs.io/en/latest/functions.html#Page.get_texttrace)
y [renderizado](https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_pixmap).

## Relación con la clase 14 y límites

Se aplica separación entre instrucciones y datos, plan fijo, validación en
ejecución, privilegio mínimo y trazas (sesión 14, pp. 15–17 y 24–25).
La contención del cliente dedicado no depende de que el detector identifique
cada ataque: carece de intérprete de acciones, y el sandbox limita red/escritura.

El detector sigue siendo heurístico y puede omitir ataques o marcar citas
educativas legítimas. No cubre todas las imágenes, idiomas, ofuscaciones,
documentos extensos ni instrucciones indirectas. Los límites de inspección
son 16 MiB, 100 páginas y 10.000 spans por página; un fallo exige revisión.
Una página escaneada no se declara segura por no tener texto extraíble.
La lectura literal no equivale a una recomendación para ejecutar su contenido.

Copilot conserva su propio agente y herramientas: no se presenta como cliente
aislado ni evaluado adversarialmente. Un LLM real y OCR permanecen fuera de
esta implementación. No se añade autenticación productiva ni nuevas herramientas.

[Arquitectura](arnes-f9-2.md) · [Validación y operación](validacion-dev-f9-2.md).
