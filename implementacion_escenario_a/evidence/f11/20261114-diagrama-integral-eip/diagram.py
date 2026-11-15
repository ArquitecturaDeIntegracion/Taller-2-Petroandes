"""Mapa EIP integral con carriles, patrones y controles locales diferenciados."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from math import atan2,cos,sin
BASE=Path(__file__).resolve().parent
ASSETS=BASE.parent/'eip_petroandes_qa/assets'
S=3
im=Image.new('RGB',(1800*S,1050*S),'white'); d=ImageDraw.Draw(im)
INK='#183245'; BLUE='#24577E'; GRAY='#657381'
def text(x,y,t,size=16,bold=False,color=INK):
    font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size*S)
    d.multiline_text((x*S,y*S),t,font=font,fill=color,anchor='mm',align='center',spacing=3*S)
def line(points,color=GRAY,dash=False):
    for a,b in zip(points,points[1:]):
        if dash:
            dist=((b[0]-a[0])**2+(b[1]-a[1])**2)**.5
            for k in range(0,int(dist),10):
                end=min(k+6,dist)
                d.line([(S*(a[0]+(b[0]-a[0])*v/dist),S*(a[1]+(b[1]-a[1])*v/dist)) for v in (k,end)],fill=color,width=3)
        else: d.line([(a[0]*S,a[1]*S),(b[0]*S,b[1]*S)],fill=color,width=4)
    a,b=points[-2:]; ang=atan2(b[1]-a[1],b[0]-a[0])
    d.polygon([(b[0]*S,b[1]*S),*((S*(b[0]-9*cos(ang+v)),S*(b[1]-9*sin(ang+v))) for v in (-.4,.4))],fill=color)
def lane(y,title):
    d.rectangle((12*S,y*S,1788*S,(y+22)*S),fill='#E8F0F5')
    font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',17*S)
    d.text((22*S,(y+2)*S),title,font=font,fill=INK)
def node(col,y,id,title,body,icon=None,pattern=None):
    x=18+col*222; w=204; h=112
    fill='#F5F8FA' if icon else '#F0F2F4'
    d.rounded_rectangle((x*S,y*S,(x+w)*S,(y+h)*S),5*S,fill,'#A8BAC8',3)
    text(x+18,y+13,id,13,True)
    if icon:
        p=next(ASSETS.glob(icon+'.*')); pic=Image.open(p).convert('RGBA')
        ratio=min(54*S/pic.width,28*S/pic.height)
        pic=pic.resize((int(pic.width*ratio),int(pic.height*ratio)),Image.Resampling.NEAREST)
        im.paste(pic,(int((x+w/2)*S-pic.width/2),int((y+4)*S)),pic)
    text(x+w/2,y+45,title,16,True)
    text(x+w/2,y+81,body,15)
    if pattern: text(x+w/2,y+131,pattern,13,color=GRAY)
def chain(y,start=0,end=7):
    for c in range(start,end): line([(18+c*222+204,y+58),(18+(c+1)*222,y+58)])

lane(0,'A  Gobierno y propagación bajo demanda   |   decisiones humanas y derivados separados')
admin=[('A1','Revisión humana','Hash, grupo, ámbito,\nuso y período',None),
 ('A2','Channel Adapter','CLI F2 y F10\nregistrar / decidir','ChannelAdapter'),
 ('A3','Message Store','SQLite: catálogo,\ndecisiones + outbox','MessageStore'),
 ('A4','Event Message','Evento y decisión\nen misma transacción','EventMessage'),
 ('A5','Idempotent Receiver','F10: propagar, reintentar\ny confirmar tras activar','IdempotentReceiver'),
 ('A6','Publicación atómica','Verificar generación\ny activar manifiesto',None),
 ('A7','Operaciones F10','Reindexar, comparar,\nrevertir con gobierno',None),
 ('A8','Message Store','Historia: revisiones,\nhuellas y recibos','MessageStore')]
for c,(id,t,b,ic) in enumerate(admin): node(c,38,id,t,b,ic)
chain(38,0,5); line([(1350,96),(1332,96)]); line([(1332,96),(1340,96),(1340,165),(1674,165),(1674,150)])
text(1170,182,'G  Catálogo autoritativo: gobierna publicación, búsqueda, lectura directa y rollback',14,True)

lane(195,'B  Ingesta PDF y publicación   |   Pipes and Filters   |   datos documentales no confiables')
ingest=[('B1','Fuentes conservadas','19 PDF; Markdown solo\ncontrasta la extracción',None),
 ('B2','Channel Adapter','Carga operada por CLI\ny preparación privada','ChannelAdapter'),
 ('B3','Message Translator','pypdf → contratos\nPydantic canónicos','MessageTranslator'),
 ('B4','Splitter','Secciones, filas, padres,\norden, páginas y chunks','Sequencer'),
 ('B5','Content Enricher','Contexto autorizado,\nprocedencia y metadatos','DataEnricher'),
 ('B6','Detector F9.2','Unicode / URL / base64;\nPyMuPDF y píxeles',None),
 ('B7','Modelo E5 fijado','384 dim, prefijos\nquery: / passage: y L2',None),
 ('B8','Filtro y publicación','G → elegibles → E5;\nQdrant, SQLite y manifiesto','Filter')]
for c,(id,t,b,ic) in enumerate(ingest): node(c,233,id,t,b,ic)
chain(233)
line([(564,345),(564,368),(680,368)],'#984A3B')
text(1120,369,'B9  Invalid Message Channel · revisión / cuarentena; bloquear activación incompleta',14,color='#984A3B')
text(332,369,'Canonical Data Model  contratos comunes',14,True)

lane(390,'C  buscar_documentos   |   Request Reply por stdio   |   las ramas híbridas se ejecutan por turnos')
query=[('C1','Clientes MCP','Inspector web 6274;\nVS Code y Copilot',None),
 ('C2','Message Endpoint','Adaptador MCP stdio\ny JSON Schema','MessageEndpoint'),
 ('C3','Router por herramienta','buscar_documentos /\nobtener_fragmento',None),
 ('C4','Message Filter','G → identidad, hash,\ngrupo, ámbito, uso, reloj','Filter'),
 ('C5','Scatter Gather local','E5/Qdrant + BM25;\ncódigos y versiones','BroadcastAggregate'),
 ('C6','Aggregator','RRF; deduplicación,\nprefiltro y desempate','Aggregator'),
 ('C7','Content Enricher','Expandir contexto\ny revalidar gobierno','DataEnricher'),
 ('C8','Filtros F6','Señales → descarte;\nsuficiencia, citas literales','ContentFilter')]
for c,(id,t,b,ic) in enumerate(query): node(c,428,id,t,b,ic)
chain(428)
text(310,562,'D  Ruta directa desde el router',14,True)
text(1360,562,'I  B8 alimenta ambas ramas; F6 usa señales B6 y reescanea el texto',14,True)

lane(585,'D  Obtención directa, contrato público y auditoría obligatoria   |   datos recibidos nunca conceden permisos')
direct=[('D1','obtener_fragmento','Código, versión, sección;\nhash / parte opcionales',None),
 ('D2','Message Filter','Misma elegibilidad G;\nambiguo o denegado','Filter'),
 ('D3','Lectura y contexto','Partes ordenadas; texto\nliteral no confiable',None),
 ('D4','Message Translator','JSON estructurado; citas,\nestado, revisión y generación','MessageTranslator'),
 ('D5','Correlation Identifier','UUID común a llamada,\nrespuesta y recibo','CorrelationIdentifier'),
 ('D6','Message Store','AuditReceipt: iniciado →\ncompletado con fsync','MessageStore'),
 ('D7','Request Reply','Cierre durable previo;\nfallo de auditoría → error','RequestReply'),
 ('D8','Clientes y plan fijo','Emisor recibe; dedicado:\n≤10 lecturas, sin LLM',None)]
for c,(id,t,b,ic) in enumerate(direct): node(c,623,id,t,b,ic)
chain(623)
line([(562,540),(562,574),(120,574),(120,623)],BLUE)
line([(1774,485),(1784,485),(1784,614),(787,614),(787,623)],BLUE)
text(888,759,'T  Toda tools/call inicia recibo antes de validar. Se guarda metadata y hashes, sin consulta ni texto; sin escritura no se entrega evidencia.',15,True)

lane(785,'E  Validación, aislamiento y entrega   |   contextos internos de prueba, sin otro servidor público')
tests=[('E1','Test Message','Anexo real; 12 PDF nuevos;\n23 casos sintéticos F9.1',None),
 ('E2','Controlador F9.2','Host: receptor TCP propio,\nsondas + / − y limpieza',None),
 ('E3','f9 sandbox','UID 10001, red none, RO;\n2 CPU, 2 GiB, 128 PID',None),
 ('E4','Cuatro fases','F9 original; MCP real;\nPDF real; dispatcher',None),
 ('E5','Wire Tap','Captura explícita F8/F9:\nentradas, trazas, salidas','WireTap'),
 ('E6','Evaluador F8','laya: soporte por afirmación\ny pertinencia por fragmento',None),
 ('E7','Message Store','Reportes, inventarios,\nF11 y paquetes previos','MessageStore'),
 ('E8','Fronteras del ensayo','Baseline y reserva intactos;\nCopilot no evaluado',None)]
for c,(id,t,b,ic) in enumerate(tests): node(c,823,id,t,b,ic)
chain(823,0,4); line([(1110,882),(1120,882),(1120,966),(1452,966),(1452,935)])
line([(1332,882),(1350,882)])
text(650,966,'E4 ejercita B, C y D en copias privadas; E6 pertenece a F8 y no es una fase del ataque F9.',15,True)
text(900,1001,'Línea continua  flujo local / llamada    ·    G I T  vínculos compartidos documentados    ·    Cruces sin punto  sin unión',15)
text(900,1027,'Iconos EIP oficiales: Hohpe y Woolf, CC BY 4.0. Cajas grises: recursos o controles propios, no nuevos patrones. Sin broker ni colas de consulta.',14)
im.save(BASE/'diagrama_integral.png',dpi=(400,400))
