"""Despliegue real y ampliación interna de cada proceso MCP de demostración."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from math import atan2,cos,sin
BASE=Path(__file__).resolve().parent; S=3
im=Image.new('RGB',(1800*S,1120*S),'white'); d=ImageDraw.Draw(im)
INK='#1D354A'; BLUE='#246C9B'; PURPLE='#7652A2'; GREEN='#387B62'; GRAY='#697985'; ORANGE='#9D602D'
def rect(box,fill='#FFFFFF',outline='#AFBFCA',radius=7,width=2):
 d.rounded_rectangle(tuple(int(v*S) for v in box),radius*S,fill,outline,int(width*S))
def text(x,y,t,size=18,bold=False,color=INK):
 f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size*S)
 d.multiline_text((x*S,y*S),t,font=f,fill=color,anchor='mm',align='center',spacing=5*S)
def icon(name,x,y,w=44):
 p=Image.open(BASE/'icons'/f'{name}.png').convert('RGBA'); p.thumbnail((w*S,w*S),Image.Resampling.LANCZOS)
 im.paste(p,(int(x*S-p.width/2),int(y*S-p.height/2)),p)
def arrow(points,color=BLUE,dashed=False,both=False):
 for a,b in zip(points,points[1:]):
  if dashed:
   length=((b[0]-a[0])**2+(b[1]-a[1])**2)**.5
   for start in range(0,int(length),12):
    d.line([(S*(a[0]+(b[0]-a[0])*v/length),S*(a[1]+(b[1]-a[1])*v/length)) for v in (start,min(start+7,length))],fill=color,width=4)
  else:d.line([(a[0]*S,a[1]*S),(b[0]*S,b[1]*S)],fill=color,width=5)
 def head(a,b):
  ang=atan2(b[1]-a[1],b[0]-a[0]);d.polygon([(b[0]*S,b[1]*S),*((S*(b[0]-11*cos(ang+v)),S*(b[1]-11*sin(ang+v))) for v in (-.42,.42))],fill=color)
 head(points[-2],points[-1])
 if both:head(points[1],points[0])
def label(x,y,t,color=GRAY,size=16):
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size*S); w=d.textlength(t,font=font)/S
 rect((x-w/2-4,y-13,x+w/2+4,y+13),'white','white',0,1);text(x,y,t,size,color=color)
def node(x,y,w,h,title,body,icons=(),fill='#FFFFFF'):
 rect((x,y,x+w,y+h),fill)
 if icons:
  for i,name in enumerate(icons):icon(name,x+w/2+(i-(len(icons)-1)/2)*57,y+32,42)
 title_y=y+65 if icons else y+25
 text(x+w/2,title_y,title,20,True)
 lines=body.count('\n')+1
 body_y=title_y+32+(lines-1)*11
 text(x+w/2,body_y,body,18)

rect((8,8,1792,1090),'#FFFFFF','#637C90',10,2)
text(290,33,'EQUIPO DEL ESTUDIANTE  ·  WINDOWS',21,True)
rect((350,60,1772,1045),'#F7FAFC','#337CAC',8,2)
icon('docker',389,85,43);icon('linux',442,85,37)
text(1020,85,'DOCKER DESKTOP  ·  MOTOR LINUX  ·  IMAGEN petroandes-educativo:local',22,True)

node(27,120,280,135,'1  Proyecto y corpus','PDF originales; código\nconfiguración y decisiones',('powershell',))
node(380,125,400,165,'2  Trabajo CLI  ·  perfil dev','Python 3.12: pypdf / PyMuPDF\nPydantic, partición y gobierno',('python','pydantic'))
node(835,125,410,165,'3  Volumen artifacts','SQLite gobierno / outbox / staging\nQdrant local + SQLite/BM25\nManifiestos de generación',('sqlite','qdrant'))
node(1320,125,410,165,'Volumen model-cache','E5 small y laya multilingüe\nPesos locales fijados por revisión',('huggingface','pytorch'))
arrow([(307,200),(380,200)]);label(344,176,'COPY',size=15)
arrow([(780,215),(835,215)]);label(807,190,'activa',size=15)
text(1040,310,'Ruta operativa persistente: el catálogo autoriza antes de publicar',17,True)

node(27,400,280,137,'VS Code con Copilot','Cliente MCP del host\nConfig .vscode/mcp.json',('vscode','mcp'))
node(380,370,400,165,'A  Contenedor dev  ·  MCP','Python -m petroandes.demo\nstdio; /tmp privado por proceso',('docker','python','mcp'))
arrow([(307,468),(340,468),(340,452),(380,452)],PURPLE,both=True)
label(350,351,'5 consulta / 6 respuesta por stdio',PURPLE)

node(27,635,280,140,'Navegador del host','MCP Inspector web\nhttp://127.0.0.1:6274',('mcp',))
node(380,600,400,190,'B  Contenedor inspector-web','Node.js 22: interfaz y proxy\nPython: petroandes.demo hijo\nstdio interno; otro /tmp privado',('docker','nodejs','python'))
arrow([(307,705),(380,705)],PURPLE,both=True)
label(344,579,'HTTP 6274 en loopback',PURPLE)

# Ampliación del interior compartido como código, nunca como almacenamiento.
rect((825,350,1732,795),'#EDF4F8','#6B97B4',7,2)
text(1277,373,'INTERIOR DE CADA PROCESO MCP EN A O B  ·  NO ES OTRO CONTENEDOR',18,True)
node(850,407,250,140,'4a  Preparar demo','Snapshot 15 + PDF\nExtraer y revisar señales',('python','pydantic'))
node(1142,407,244,140,'4b  Modelo E5','Elegibles → embeddings\n384 dimensiones, CPU',('huggingface','pytorch'))
node(1428,407,280,140,'4c  /tmp privado','Catálogo SQLite + Qdrant\nProyección SQLite/BM25',('sqlite','qdrant'))
arrow([(1100,475),(1142,475)]);arrow([(1386,475),(1428,475)])
arrow([(1525,290),(1525,332),(1745,332),(1745,394),(1264,394),(1264,407)],GREEN,dashed=True)
label(1395,332,'pesos montados',GREEN)
node(850,615,250,140,'5a  Entrada MCP','Dos contratos de lectura\nIDs autorizados y filtros',('mcp','python'))
node(1142,615,244,140,'5b  Búsqueda y F6','E5 + BM25 → RRF\nFiltrar señales y citar',('qdrant','sqlite'))
node(1428,615,280,140,'6  Resultado y recibo','Citas / abstención / error\nobtener: lectura literal',('mcp','python'))
arrow([(1100,681),(1142,681)]);arrow([(1386,681),(1428,681)])
arrow([(1568,547),(1568,574),(975,574),(975,615)])
label(1255,574,'generación privada y política vigente')
arrow([(975,615),(975,597),(1568,597),(1568,615)])
label(1265,597,'obtener_fragmento: ruta directa',size=15)
arrow([(780,452),(825,452)],GRAY,dashed=True)
arrow([(780,700),(825,700)],GRAY,dashed=True)
text(1277,775,'A y B ejecutan este mismo núcleo; no comparten la carpeta Qdrant local.',17,True)

node(27,875,280,140,'Controlador F9 en host','PowerShell / Python\ntools/f9_validate.py',('powershell','python'))
node(380,855,400,170,'f9-sandbox  ·  perfil dev','Cliente restringido → MCP\nÍndices temporales; UID 10001\nRed none, fuente/pesos RO',('docker','python','pytest'))
node(835,855,410,170,'Evaluación F8 en dev','laya-multilingual en CPU\nEvalúa soporte y pertinencia\nSe ejecuta fuera de la consulta',('huggingface','pytorch','pytest'))
node(1320,855,410,170,'reports/portable  ·  bind RW','Recibos MCP por correlation_id\nEvidencias F8 / F9.2 y entrega\nPersisten en el host',('python',))
arrow([(307,947),(380,947)],ORANGE)
arrow([(780,960),(802,960),(802,1040),(1530,1040),(1530,1025)],ORANGE)
arrow([(1245,960),(1320,960)],ORANGE)
arrow([(1568,755),(1568,855)])
label(1568,824,'JSON antes de responder')
text(1050,1068,'Fuente del servicio dev RO  ·  pesos en model-cache  ·  artifacts persistente operativo  ·  salida de prueba propia RW',17)
text(900,1110,'AZUL  datos y derivados     MORADO  interacción cliente MCP     VERDE  montaje de pesos     NARANJA  validación     GRIS  ampliación del interior',17,True)
im.save(BASE/'despliegue.png',dpi=(400,400))
