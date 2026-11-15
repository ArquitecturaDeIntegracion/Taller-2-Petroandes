"""Despliegue de punta a punta con iconos de tecnología y explicación operativa."""
from pathlib import Path
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]
prefix=(ROOT/'tmp/f9_2_documento/build.py').read_text(encoding='utf-8').split("doc.add_heading('Funcionamiento del arnés F9.2',0)")[0]
prefix=prefix.replace('Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx','Despliegue_PetroAndes_Flujo_Completo_Tecnologias.docx')
exec(compile(prefix,'estilos','exec'))
from docx.shared import Mm
from docx.enum.section import WD_ORIENT
s.orientation=WD_ORIENT.LANDSCAPE; s.page_width=Mm(420); s.page_height=Mm(297)
s.top_margin=s.bottom_margin=Mm(11); s.left_margin=s.right_margin=Mm(12)
doc.styles['Title'].font.size=Pt(23)
footer.runs[0].text='PetroAndes  ·  Despliegue y flujo de información  |  '
doc.core_properties.title='Despliegue de PetroAndes desde la ingesta hasta la consulta MCP'
doc.core_properties.subject='Despliegue actual Docker y tecnologías del sistema documental con F9.2 y F8'
doc.add_heading('Despliegue de PetroAndes y flujo de información',0)
p('De la ingesta PDF a la consulta MCP  ·  Tecnologías y límites de ejecución actuales  ·  14 de noviembre de 2026')
para=p(''); para.alignment=WD_ALIGN_PARAGRAPH.CENTER
pic=para.add_run().add_picture(str(BASE/'despliegue.png'),width=Inches(14.5))
pic._inline.docPr.set('descr','Equipo Windows con VS Code, navegador y PowerShell. Docker Desktop ejecuta trabajos dev, servidor MCP para VS Code, contenedor Inspector web y sandbox F9. Volúmenes model-cache y artifacts y reportes bind. Cada proceso demo prepara SQLite y Qdrant privados. El flujo numerado va del PDF a embeddings, índice, consulta, respuesta y recibo. Laya se ejecuta aparte en F8.')
p('Plano basado en compose.yaml, Dockerfile y las configuraciones reales de Inspector y VS Code. El recuadro interior derecho amplía '
  'el proceso de cada instancia A/B; no representa un tercer contenedor ni una base Qdrant compartida.','Caption')
page('Cómo recorre la información el despliegue')
h('Preparación y persistencia')
lead('1 Construir y preparar.', 'El proyecto vive en el equipo Windows y Docker Desktop ejecuta contenedores Linux. '
     'La construcción copia el corpus y los documentos de referencia a la imagen petroandes-educativo:local. '
     'En dev, el código del proyecto se monta en solo lectura; los reportes se montan con escritura. '
     'Docker Compose declara los volúmenes model-cache y artifacts. El peso de E5 y el de laya se preparan una vez '
     'y las ejecuciones documentadas los consumen desde caché.')
lead('2 Ingerir PDF.', 'Los trabajos CLI del perfil dev usan Python 3.12, pypdf, PyMuPDF y Pydantic. '
     'Extraen secciones, páginas, tablas y texto, contrastan con Markdown y crean fragmentos con hash y procedencia. '
     'F9.2 incorpora señales de instrucciones maliciosas y propiedades visuales sospechosas del PDF. '
     'El documento original se conserva; un resultado dudoso requiere revisión.')
lead('3 Publicar derivados operativos.', 'El catálogo SQLite autoriza por hash, grupo, ámbito, uso y período. '
     'Solo los documentos elegibles se vectorizan con multilingual-e5-small, Sentence Transformers y PyTorch en CPU '
     '(384 dimensiones). La publicación completa contiene Qdrant local, catálogo de fragmentos, proyección léxica '
     'SQLite/BM25 y manifiestos. F10 registra eventos y decisiones conjuntamente, propaga bajo demanda y confirma '
     'tras activar una generación verificada. Esta ruta persistente usa artifacts.')
lead('4 Preparar la demostración.', 'petroandes.demo reutiliza esos módulos, pero copia el snapshot aprobado de revisión 15 '
     'y construye su catálogo e índices dentro de un temporal privado por proceso. Su reloj histórico reproduce '
     'la aprobación del 8 de noviembre de 2026: 19 PDF y 92 fragmentos preparados, 14 documentos y 68 fragmentos publicados. '
     'No toma como índice de presentación la carpeta operativa artifacts. Al finalizar el proceso se eliminan sus temporales.')
h('Consulta desde las dos interfaces MCP')
table(('Ruta de acceso','Despliegue y transporte','Qué ocurre al consultar'),[
    ('A VS Code y GitHub Copilot','VS Code ejecuta docker compose --profile dev run ... dev -m petroandes.demo. '
     'El cliente y el proceso Python intercambian MCP por stdio a través de Docker CLI.',
     'Se negocian las dos herramientas. La primera operación prepara la demo privada; las siguientes reutilizan esa preparación mientras viva el proceso.'),
    ('B MCP Inspector web','El navegador usa HTTP hacia 127.0.0.1:6274. El contenedor inspector-web ejecuta '
     'Node.js 22 y lanza petroandes.demo como hijo Python mediante stdio interno.',
     'El usuario envía argumentos JSON desde la web. El servidor hijo tiene su propio catálogo e índice temporal, distinto del iniciado por VS Code.')
],(2.0,6.3,7.29))
lead('5 Buscar u obtener.', 'buscar_documentos recibe consulta, top_k y filtros; calcula primero IDs autorizados, '
     'consulta E5/Qdrant y BM25, fusiona rankings con RRF y aplica el compositor extractivo F6. Los códigos exactos '
     'y versiones precisan la selección. F6 excluye unidades señaladas y exige contexto y citas. '
     'obtener_fragmento usa la misma política y devuelve partes literales ordenadas por código, versión y sección; '
     'no necesita la búsqueda híbrida ni la composición F6.')
lead('6 Registrar y devolver.', 'La respuesta contiene estado, citas, evidencia, revisión de gobierno, generación '
     'y correlation_id. La auditoría escribe un recibo antes de entregar evidencia; si falla la persistencia, '
     'la llamada devuelve auditoria_no_disponible. Los recibos habituales se guardan en reports/portable/mcp-audit/. '
     'Las respuestas vuelven por stdio al cliente MCP o por el proxy de Inspector al navegador. Qdrant es embebido: '
     'no hay servidor Qdrant ni puerto 6333 en este despliegue, y el servidor MCP de presentación no expone HTTP propio.')
h('Evaluación y contención fuera de la consulta habitual')
p('F8 carga laya multilingüe con PyTorch en CPU para evaluar soporte de afirmaciones y pertinencia de fragmentos. '
  'Laya no participa en las consultas normales ni detecta el ataque en F9.2. El controlador F9 del host inicia '
  'f9-sandbox: cliente restringido, servidor y datos de prueba temporales; red none, UID 10001, capacidades vacías, '
  'no-new-privileges, fuente y pesos RO, 2 CPU, 2 GiB, 128 procesos y temporal acotado. Solo la carpeta propia de '
  'salida admite escritura persistente. Las sondas usan además un receptor Docker efímero en una red interna separada. '
  'El sandbox no monta el socket Docker ni artifacts persistentes.')
p('La evidencia conservada verifica 255 pruebas y las cuatro fases de F9.2. El detector es heurístico y no utiliza OCR. '
  'Copilot conserva sus capacidades del IDE; su resistencia adversarial no se acredita con el cliente restringido. '
  'Los iconos de Hugging Face representan los modelos locales y su ecosistema; no implican una llamada a un servicio alojado durante la consulta.')
para=p('Fuentes del despliegue  ','Caption')
for i,(label,target) in enumerate([('Compose','../../implementacion_escenario_a/compose.yaml'),
    ('Dockerfile','../../implementacion_escenario_a/Dockerfile'),('Demo','../../implementacion_escenario_a/petroandes/demo.py'),
    ('VS Code','../../implementacion_escenario_a/.vscode/mcp.json'),('Inspector','../../implementacion_escenario_a/config/inspector-web.json')]):
    if i:para.add_run('  ·  ')
    link(para,label,target)
para=p('Iconografía  ','Caption')
link(para,'Devicon','https://github.com/devicons/devicon'); para.add_run(' (MIT)  ·  ')
link(para,'Simple Icons','https://github.com/simple-icons/simple-icons'); para.add_run(' (CC0). Logotipos y marcas de sus respectivos titulares. '
    'E5, laya y BM25 se identifican por texto; no se inventan logotipos de esos modelos o algoritmos.')
OUT.parent.mkdir(parents=True,exist_ok=True); doc.save(OUT); print(OUT)
