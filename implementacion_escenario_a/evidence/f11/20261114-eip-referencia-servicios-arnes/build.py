"""Plano de iconos abiertos y explicación de dos herramientas y arnés en dos páginas."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
prefix=(ROOT/'tmp/f9_2_documento/build.py').read_text(encoding='utf-8').split("doc.add_heading('Funcionamiento del arnés F9.2',0)")[0]
prefix=prefix.replace('Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx','Arquitectura_EIP_Servicios_MCP_y_Arnes_PetroAndes.docx')
exec(compile(prefix,'estilos','exec'))
from docx.shared import Mm
from docx.enum.section import WD_ORIENT
s.orientation=WD_ORIENT.LANDSCAPE; s.page_width=Mm(420); s.page_height=Mm(297)
s.top_margin=s.bottom_margin=Mm(10); s.left_margin=s.right_margin=Mm(12)
doc.styles['Title'].font.size=Pt(20)
footer.runs[0].text='PetroAndes  ·  Servicios MCP y arnés F9.2  |  '
doc.core_properties.title='Arquitectura EIP de los servicios MCP y el arnés de PetroAndes'
doc.add_heading('Arquitectura EIP de los servicios MCP y el arnés F9.2',0)
p('Plano actualizado con el estilo de la referencia visual  ·  Estado documentado al 14 de noviembre de 2026')
para=p(''); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.space_after=Pt(0)
pic=para.add_run().add_picture(str(BASE/'diagrama.png'),width=Inches(13.2))
pic._inline.docPr.set('descr','Diagrama EIP con iconos abiertos y cuatro bandas: preparación y gobierno; buscar_documentos y obtener_fragmento en una conexión MCP; administración F10 y auditoría obligatoria; arnés F9.2 con cliente restringido, sandbox y captura de evidencia.')
p('EIP de Gregor Hohpe y Bobby Woolf. Iconos oficiales CC BY 4.0, diagrama propio adaptado a la referencia aportada. '
  'Los patrones describen llamadas locales y flujos de datos; no implican un broker ni colas de consulta.','Caption')
page('Funcionamiento de las rutas y del arnés')
h('A Preparación y gobierno documental')
p('El operador carga los 19 PDF mediante F3. El Channel Adapter adapta archivos al flujo de ingesta; Message Translator convierte '
  'el PDF en contratos Pydantic de documento, sección, tabla y fragmento. Content Enricher añade hash, gobierno, procedencia, '
  'contexto y señales de seguridad. Splitter conserva secciones, padres, filas, páginas y orden. Markdown se usa para contrastar '
  'la extracción. Una extracción dudosa produce un informe de revisión o cuarentena, representado como Invalid Message Channel.')
p('El registro SQLite decide la elegibilidad por hash, grupo, ámbito, uso y período. La similitud no concede permisos. '
  'El publicador filtra antes de vectorizar y activa una generación completa con manifiesto verificado, proyección densa Qdrant local '
  'y proyección léxica SQLite/BM25. El bundle E5 produce vectores de 384 dimensiones y está fijado por revisión y huellas. '
  'La demo privada parte de 92 fragmentos preparados y publica 68 fragmentos de 14 documentos autorizados en la revisión 15 histórica.')
h('B Dos herramientas del mismo servidor MCP')
p('La conexión se llama petroandes. El adaptador Message Endpoint recibe herramientas por stdio y valida JSON Schema. '
  'El nombre implementado de la búsqueda es buscar_documentos. Ambas herramientas comparten gobierno; los parámetros no pueden '
  'cambiar grupos, perfil, finalidad ni reloj. El resultado vuelve al cliente que inició la llamada mediante Request Reply.')
table(('Herramienta','Parámetros de entrada','Ruta y resultado'),[
    ('buscar_documentos','consulta; top_k de 1 a 10; filtros opcionales por tipo, activo o tramo.',
     'Ruta superior del plano. Prefiltra IDs autorizados y consulta E5/Qdrant y BM25. Scatter Gather es una correspondencia local: las ramas corren por turnos. Aggregator fusiona rankings con RRF; códigos exactos y versiones precisan la selección. F6 descarta unidades señaladas, reconstruye contexto y produce extractos con citas o una abstención.'),
    ('obtener_fragmento','doc_id; version_documental como cadena o null; section_id; hash o parte opcionales.',
     'Ruta directa inferior del plano. Selecciona partes ordenadas bajo la misma elegibilidad, sin ejecutar búsqueda híbrida ni composición F6. Devuelve lectura literal autorizada como dato no confiable; si falta autorización, deniega sin contenido. La lectura del anexo permite inspección, no autoriza sus instrucciones.')
],(1.65,3.6,10.34))
h('C Administración F10 y auditoría de cada consulta')
p('La revisión humana registra decisiones vinculadas al hash. Event Message representa el evento del outbox SQLite registrado '
  'junto con la decisión; Idempotent Receiver representa la propagación F10 bajo demanda. El sistema verifica y activa una generación '
  'antes de confirmar el evento. Repetir un evento confirmado no repite efectos; reindexar o revertir derivados no restaura permisos revocados.')
p('La auditoría MCP funciona en todas las llamadas, aunque no se ejecute el arnés. Correlation Identifier vincula el UUID de la respuesta '
  'con su recibo. Message Store conserva un registro iniciado y después completado mediante flush/fsync y reemplazo atómico. '
  'Incluye contexto, hashes, revisión, generación, señales y chunks descartados; omite consulta, texto y credenciales. '
  'Si no puede escribir, devuelve auditoria_no_disponible sin evidencia. No debe confundirse esta auditoría obligatoria con Wire Tap, '
  'que captura evidencia adicional solo durante los ensayos.')
h('D Arnés F9.2 y escenario del documento envenenado')
p('El controlador tools/f9_validate.py se ejecuta en el host, prepara un receptor TCP ficticio y comprueba conectividad positiva '
  'antes y después. El worker f9-sandbox corre con UID 10001, red none, fuente y pesos de solo lectura, capacidades vacías y '
  'no-new-privileges. Solo la salida de la corrida admite escritura persistente. El cliente MCP dedicado congela un plan de hasta '
  'diez lecturas antes de recibir documentos; valida contrato, literalidad y citas. No usa un LLM ni interpreta acciones del texto.')
p('El detector F9.2 revisa Unicode, instrucciones de sustitución o suplantación, ocultación y envío externo, además de variantes URL/base64. '
  'PyMuPDF inspecciona texto invisible, microscópico, fuera de página o sin contraste. Las señales se incorporan en la ingesta y se '
  'consultan de nuevo al componer. El PDF original y el anexo se conservan. El arnés ejecuta cuatro fases: ataque original, fronteras MCP '
  'reales, doce PDF nuevos por el flujo real y dispatcher sintético F9.1. Wire Tap recoge trazas, entradas y resultados; Message Store '
  'guarda la evidencia. F8 usa laya para evaluar respaldo y pertinencia por separado; laya no es una fase del ataque F9. F11 prepara la entrega.')
lead('Resultado esperado del ataque.', 'Al buscar el anexo de COM-PRV-0134, se observa su recuperación y descarte y la respuesta se abstiene. '
     'La obtención directa autorizada conserva el texto íntegro para auditoría. La consulta legítima de firmware devuelve 7.4 y condiciones con citas. '
     'La abstención por sí sola no prueba la causa: también interviene la regla de intención no admitida; se comprueba el chunk objetivo en la traza. '
     'El cliente restringido no convierte órdenes del anexo en acciones.')
lead('Evidencia y límites.', 'La validación Docker dev conservada aprobó 255 pruebas y las cuatro fases. En los doce PDF nuevos se detectaron '
     'siete adversariales y cinco benignos respondieron sin falsos positivos en ese conjunto; se generaron 24 llamadas y 26 recibos. '
     'El detector es heurístico, sin OCR ni garantía universal. Copilot y un LLM real siguen sin evaluación adversarial; el sandbox no aísla el IDE. '
     'La reserva formal no se ejecutó.')
para=p('Reportes y fuentes  ','Caption')
link(para,'Guía F9.2 y rutas de reportes','../../implementacion_escenario_a/docs/validacion-dev-f9-2.md'); para.add_run('  ·  ')
link(para,'Evidencia Docker','../../implementacion_escenario_a/evidence/f9/20261114-arnes-contenido/README.md'); para.add_run('  ·  ')
link(para,'Enterprise Integration Patterns','https://www.enterpriseintegrationpatterns.com/patterns/messaging/')
OUT.parent.mkdir(parents=True,exist_ok=True); doc.save(OUT); print(OUT)
