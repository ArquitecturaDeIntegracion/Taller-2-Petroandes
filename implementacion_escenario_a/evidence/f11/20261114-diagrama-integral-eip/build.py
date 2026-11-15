"""Dos páginas A3 horizontales: plano integral y correspondencia de todos sus elementos."""
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
prefix=(BASE.parent/'f9_2_documento/build.py').read_text(encoding='utf-8').split("doc.add_heading('Funcionamiento del arnés F9.2',0)")[0]
prefix=prefix.replace('Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx','Diagrama_Integral_EIP_PetroAndes_Actual.docx')
exec(compile(prefix,'estilos','exec'))
from docx.shared import Mm
from docx.enum.section import WD_ORIENT
s.orientation=WD_ORIENT.LANDSCAPE
s.page_width=Mm(420); s.page_height=Mm(297)
s.left_margin=s.right_margin=Mm(12)
s.top_margin=s.bottom_margin=Mm(12)
footer.runs[0].text='PetroAndes  ·  Diagrama integral EIP  ·  F9.2  |  '
doc.core_properties.title='Diagrama integral EIP de la arquitectura actual de PetroAndes'
doc.core_properties.subject='Arquitectura completa del servicio con gobierno, ingesta, MCP, F10 y F9.2'
doc.add_heading('Diagrama integral EIP de PetroAndes',0)
p('Arquitectura completa implementada del Escenario A con F9.2  ·  14 de noviembre de 2026','Subtitle')
p('El plano integra el servicio documental y sus rutas administrativas y de validación. Los IDs enlazan cada elemento con la matriz de la segunda página. '
  'Los patrones describen responsabilidades locales: no implican un broker ni ejecución distribuida. G identifica el gobierno común; I las proyecciones; T la auditoría de cada llamada.')
para=p(''); pic=para.add_run().add_picture(str(BASE/'diagrama_integral.png'),width=Mm(396))
pic._inline.docPr.set('descr','Diagrama EIP integral en cinco carriles: gobierno y eventos, ingesta y publicación, búsqueda híbrida MCP, lectura directa y auditoría, y validación con F8, F9.2 y entrega F11. Los IDs A1 a E8 se describen en la matriz.')
para.paragraph_format.space_after=Pt(1)
p('Lectura del plano  A y B preparan el estado; C y D atienden consultas; E prueba esas mismas rutas en contextos privados. '
  'Una sola conexión pública petroandes; el arnés no añade un servidor de presentación. Iconos EIP de Hohpe y Woolf, CC BY 4.0; plano propio.','Caption')
page('Matriz completa de patrones y elementos implementados')
p('La correspondencia cubre los patrones documentados en el diseño y los controles incorporados hasta F9.2. '
  'Los nombres EIP conservan su denominación oficial; los mecanismos propios se identifican expresamente. Rutas relativas a implementacion_escenario_a.')
rows=[
('A2 B2 C1 C2','Channel Adapter y Message Endpoint','Recepción por CLI y archivos; negociación MCP, tools/list y tools/call por stdio; dos herramientas de lectura. Clientes Inspector web y VS Code/Copilot.','catalog/__main__.py; extract/__main__.py; mcp_server.py; mcp_tools.py'),
('B3','Message Translator y Canonical Data Model','PDF a contratos Pydantic de documento, tabla, sección y fragmento. Texto, hash, versión o emisión, páginas y procedencia permanecen trazables.','extract/pdf.py; contracts/; chunk/'),
('A B C D','Pipes and Filters','Etapas separadas con contratos: registro, extracción, partición, enriquecimiento, publicación, elegibilidad, recuperación y composición.','catalog/; extract/; index/; retrieve/; compose/'),
('B4','Splitter','Partición structural-es-1.0.0; conserva padres e hijos, orden, cabeceras, filas y condiciones. Objetivo 250–350 tokens; máximo de entrada E5 448.','chunk/structural.py; chunk/context.py'),
('B5 C7 D3','Content Enricher','Añade metadatos de gobierno, contexto E5, procedencia y señales; expande contexto de respuesta únicamente con fragmentos autorizados.','extract/prepare.py; extract/metadata.py; retrieve/selection.py'),
('B9','Invalid Message Channel','Correspondencia local: informe de revisión o cuarentena para extracción dudosa/inválida; no es una cola. Se impide activar una generación incompleta.','extract/pipeline.py; extract/models.py; index/publication.py'),
('A3 A4','Event Message y outbox transaccional','Documento o decisión y su evento se registran en SQLite conjuntamente. Outbox es un mecanismo propio de persistencia; la propagación se inicia bajo demanda.','catalog/schema.py; catalog/decisions.py; index/propagation.py'),
('A5','Idempotent Receiver','Replay de un evento confirmado no repite efectos. Reintentos preparan y verifican una generación antes de confirmar el evento. No hay vigilancia continua.','index/propagation.py; tools/f10.py'),
('B8 C4 D2','Message Filter','La política exige hash, identidad/grupo, ámbito, uso y ventana temporal. Prefiltra publicación y ambas ramas de búsqueda; la lectura y expansión usan la misma política.','governance/eligibility.py; index/publication.py; retrieve/service.py'),
('C3','Content Based Router','Correspondencia funcional del despacho por nombre de herramienta: buscar_documentos o obtener_fragmento. El contenido del documento no elige herramientas ni privilegios.','mcp_tools.py: CONTRACTS y call_tool'),
('C5 C6','Scatter Gather y Aggregator','Búsqueda densa E5/Qdrant y léxica BM25; códigos exactos y versiones precisan selección/desempate. RRF combina rankings sin duplicados. Ramas por turnos en el proceso local.','retrieve/service.py; retrieve/ranking.py; index/projections.py'),
('C8 D4','Message Filter Content Filter y Message Translator','F6 excluye unidades con señales, verifica suficiencia y selecciona extractos con citas. El adaptador serializa el contrato; devuelve respuesta, abstención, denegación o error.','compose/service.py; compose/units.py; contracts/responses.py; mcp_tools.py'),
('D5 D7','Correlation Identifier y Request Reply','correlation_id enlaza llamada, respuesta y recibo. Las respuestas incluyen generation_id, revision_gobierno y referencias documentales; stdout se reserva al protocolo.','security/audit.py; mcp_tools.py; mcp_server.py'),
('A8 D6 E7','Message History y Message Store','Catálogo, eventos, generaciones y huellas permiten reconstruir procedencia. Recibos locales persistidos y evidencias conservan decisiones y resultados. Sin firma ni almacén inviolable.','catalog/; index/registry.py; security/audit.py; evidence/'),
('E5 E6','Wire Tap y evaluación F8','Captura explícita de entradas, rankings, respuestas y trazas al ejecutar arneses. Laya multilingüe juzga soporte por afirmación y pertinencia por fragmento; no compone la respuesta MCP.','tools/f8_evaluate.py; tools/f8_judge.py; tools/f9_observe.py; tools/f9_content_flow.py'),
('E1 E4','Test Message','Correspondencia funcional: PDF y consultas controlados ejercitan las rutas reales. F9 original, fronteras MCP, doce PDF nuevos y suite sintética F9.1 se informan por separado.','tools/f9_content_cases.py; tools/f9_content_prepare.py; tools/f9_guard_check.py'),
('A1 A3 A6 A7 B8','Recursos de gobierno y persistencia','Revisión humana; catálogo autoritativo; publicación completa y atómica; reindexación y rollback sujetos a gobierno vigente. Qdrant local con un único propietario y proyecciones SQLite/BM25.','catalog/; index/generation.py; index/publication.py; index/registry.py; tools/f10.py'),
('B1 B6 B7','Fuentes detector y representación','19 PDF originales; Markdown solo contrasta. Detector textual Unicode/URL/base64 y revisión PyMuPDF de texto invisible, fuera de página, microscópico o sin contraste. E5 small: 384 dimensiones, normalización L2.','security/detection.py; security/pdf_review.py; embeddings/; config/embedding-bundle.json'),
('D1 D3 D6 D8','Lectura auditoría y cliente restringido','Lectura directa conserva texto íntegro autorizado y no confiable. AuditReceipt persiste iniciado y completado con fsync/reemplazo atómico; falla sin evidencia si no escribe. Plan de hasta diez lecturas congelado antes de recibir datos.','retrieve/selection.py; security/audit.py; security/consumer.py; safe_client.py'),
('E2 E3 E4 E8','Contención y alcance de F9.2','Controlador host; receptor TCP ficticio y sondas; worker sin red, UID 10001, montajes RO, no-new-privileges y capacidades vacías. Solo la salida de la corrida es RW; tmpfs 1 GiB y recursos acotados.','compose.yaml; tools/f9_validate.py; tools/f9_validation_runtime.py; tools/f9_sandbox_probe.py'),
('E6 E7 E8','Evaluación entrega y fronteras','F8 conserva juicios; F11 paquetes, inventarios y evidencia. La demo usa snapshot académico revisión 15, reloj histórico, 14 documentos y 68 fragmentos. Baseline y reserva se preservan; reserva no ejecutada.','demo.py; config/mcp-demo.json; tools/f11_package.py; docs/revision/; evidence/')]
table(('IDs','Patrón o elemento','Responsabilidad y comportamiento actual','Código y artefactos petroandes salvo tools o config'),rows,(.9,3.0,7.25,4.44))
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for margin in cell._tc.get_or_add_tcPr().iter(qn('w:tcMar')):
                for item in margin:
                    if item.tag in (qn('w:top'),qn('w:bottom')): item.set(qn('w:w'),'35')
            for para in cell.paragraphs:
                para.paragraph_format.space_after=Pt(0)
                for run in para.runs: run.font.size=Pt(10)
lead('Alcance de seguridad.', 'El detector es heurístico y no utiliza OCR. Los índices antiguos requieren reingesta para señales nuevas. '
     'Una abstención no identifica por sí sola su causa: el anexo también activa la regla de intención no admitida. '
     'El arnés verifica el chunk recuperado y descartado. Copilot y un LLM real siguen sin evaluación adversarial; el sandbox del ensayo no aísla el IDE.')
para=p('Fuentes y atribución  ','Caption')
link(para,'Diseño e implementación EIP','../../implementacion_escenario_a/docs/f11-diseno-eip.md'); para.add_run('  ·  ')
link(para,'ADR F9.2','../../implementacion_escenario_a/docs/adr-0015-arnes-f9-2.md'); para.add_run('  ·  ')
link(para,'Evidencia Docker F9.2','../../implementacion_escenario_a/evidence/f9/20261114-arnes-contenido/README.md'); para.add_run('  ·  ')
link(para,'Catálogo EIP Hohpe y Woolf','https://www.enterpriseintegrationpatterns.com/patterns/messaging/')
para.add_run('  CC BY 4.0. No se atribuyen al proyecto broker, pub/sub, entrega garantizada ni colas que no están implementados.')
OUT.parent.mkdir(parents=True,exist_ok=True); doc.save(OUT); print(OUT)
