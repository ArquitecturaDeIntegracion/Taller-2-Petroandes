"""Diagramas C4 y EIP con fuentes y geometría deterministas para Word."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ASSETS = BASE.parent/'eip_petroandes_qa/assets'
S = 3
BLUE, INK, GRAY, LIGHT = '#24577E', '#183245', '#5A6874', '#EAF2F7'
FONT = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')


class Figure:
    def __init__(self, height):
        self.im = Image.new('RGB', (1000*S, height*S), 'white')
        self.d = ImageDraw.Draw(self.im)

    def rect(self, box, fill='white', outline='#B3C4D0', radius=5, width=1.5):
        self.d.rounded_rectangle(tuple(int(x*S) for x in box), radius*S, fill, outline, int(width*S))

    def text(self, xy, text, size=18, color=INK, bold=False, anchor='mm'):
        self.d.multiline_text((xy[0]*S, xy[1]*S), text,
            font=ImageFont.truetype(str(BOLD if bold else FONT), size*S), fill=color,
            anchor=anchor, align='center' if anchor=='mm' else 'left', spacing=4*S)

    def line(self, points, color=GRAY, width=1.7, arrow=True):
        self.d.line([(int(x*S),int(y*S)) for x,y in points], fill=color, width=int(width*S))
        if arrow:
            x,y=points[-1]; px,py=points[-2]
            import math
            angle=math.atan2(y-py,x-px)
            ends=[(x-10*math.cos(angle+a),y-10*math.sin(angle+a)) for a in (-.42,.42)]
            self.d.polygon([(x*S,y*S),*((a*S,b*S) for a,b in ends)], fill=color)

    def label(self, xy, text, size=17):
        font=ImageFont.truetype(str(FONT),size*S)
        b=self.d.textbbox((0,0),text,font=font)
        w=(b[2]-b[0])/S
        self.rect((xy[0]-w/2-4,xy[1]-12,xy[0]+w/2+4,xy[1]+12),outline='white',radius=0)
        self.text(xy,text,size,GRAY)

    def node(self, x,y,w,h,title,kind,detail,store=False,gray=False):
        fill = '#F0F2F4' if gray else LIGHT if store else BLUE
        ink = INK if store or gray else 'white'
        self.rect((x,y,x+w,y+h),fill,GRAY if gray else BLUE,3,1.5)
        title_size=20
        while self.d.textlength(title,font=ImageFont.truetype(str(BOLD),title_size*S))>(w-16)*S:
            title_size-=1
        self.text((x+w/2,y+23),title,title_size,ink,True)
        self.text((x+w/2,y+48),kind,16,ink)
        self.text((x+w/2,y+h-24),detail,18,ink)

    def save(self,name):
        self.im.save(BASE/(name+'.png'),dpi=(400,400))


def containers():
    f=Figure(480)
    f.rect((178,15,984,450),'#FCFDFE', '#8A9CA9',3)
    f.text((194,31),'PetroAndes  ·  frontera del sistema',18,bold=True,anchor='la')
    f.node(15,220,135,100,'Estudiante','[Persona]','Define el plan',gray=True)
    f.node(205,64,215,98,'Controlador F9.2','[Aplicación Python]','Orquesta y verifica')
    f.node(205,242,215,100,'Cliente restringido','[Aplicación Python]','Plan fijo sin LLM')
    f.node(478,242,220,100,'Servidor petroandes','[Aplicación Python]','Dos lecturas MCP')
    f.node(478,64,220,98,'Corpus y pesos','[Archivos locales]','PDF y modelo E5',store=True)
    f.node(751,64,205,98,'Gobierno documental','[SQLite]','Hash y permisos',store=True)
    f.node(751,242,205,100,'Índice privado','[Qdrant y SQLite]','Vector y BM25',store=True)
    f.node(751,345,205,100,'Recibos y reportes','[Archivos JSON]','Evidencia persistente',store=True)
    f.line([(150,270),(205,270)]); f.label((177,253),'plan',16)
    f.line([(81,220),(81,113),(205,113)]); f.label((101,170),'ensayo',16)
    f.line([(312,162),(312,242)]); f.label((312,204),'inicia y controla',16)
    f.line([(420,290),(478,290)]); f.label((449,271),'stdio',16)
    f.line([(588,162),(588,242)]); f.label((588,204),'lee e ingiere',16)
    f.line([(676,242),(721,242),(721,113),(751,113)]); f.label((721,185),'autoriza',16)
    f.line([(698,290),(751,290)]); f.label((724,270),'lee',16)
    f.line([(698,321),(726,321),(726,401),(751,401)]); f.label((724,354),'registra',16)
    f.line([(312,342),(312,401),(720,401)]); f.label((508,401),'resultados del ensayo',16)
    f.text((500,467),'Azul  aplicación    ·    Azul claro  almacén    ·    Flecha  interacción etiquetada',17,GRAY)
    f.save('c4_contenedores')


def components():
    f=Figure(440)
    f.rect((185,16,984,416),'#FCFDFE','#8A9CA9',3)
    f.text((200,34),'Servidor petroandes  ·  componentes de consulta',18,bold=True,anchor='la')
    f.node(14,195,145,104,'Cliente MCP','[Aplicación]','Plan prefijado',gray=True)
    f.node(215,92,220,102,'Entrada MCP','[mcp_tools.py]','Valida argumentos')
    f.node(473,92,220,102,'Recuperador','[retrieve/]','Permisos y ranking')
    f.node(731,92,220,102,'Compositor F6','[compose/]','Extractos o abstención')
    f.node(215,285,220,102,'Auditoría','[audit.py]','Inicio y cierre durable')
    f.node(473,285,220,102,'Detector','[detection.py]','Texto y señales PDF')
    f.line([(159,228),(184,228),(184,144),(215,144)]); f.label((181,185),'llama',16)
    f.line([(435,143),(473,143)]); f.label((453,123),'delega',15)
    f.line([(693,143),(731,143)]); f.label((712,123),'buscar',15)
    f.line([(841,194),(841,336),(693,336)]); f.label((812,281),'comprueba',16)
    f.line([(325,194),(325,285)]); f.label((325,241),'persiste antes de responder',16)
    f.line([(215,175),(173,175),(173,267),(159,267)]); f.label((102,322),'respuesta',16)
    f.text((825,392),'obtener_fragmento devuelve\nlectura literal autorizada',17,GRAY)
    f.text((500,432),'Flechas  invocaciones principales    ·    Retornos internos omitidos',17,GRAY)
    f.save('c4_componentes')


def eip():
    f=Figure(445)
    f.text((500,20),'Request Reply por stdio  ·  Pipes and Filters en llamadas síncronas',19,bold=True)
    def card(x,y,w,title,icon,detail):
        f.rect((x,y,x+w,y+140),'#FCFDFE','#A8BAC8')
        img=Image.open(ASSETS/(icon+'.gif')).convert('RGBA')
        img.thumbnail((104*S,48*S),Image.Resampling.LANCZOS)
        f.im.paste(img,(int((x+w/2)*S-img.width/2),int((y+12)*S)),img)
        f.text((x+w/2,y+79),title,20,bold=True)
        f.text((x+w/2,y+113),detail,18)
    card(16,58,208,'Channel Adapter','ChannelAdapter','MCP stdio y contratos')
    card(270,58,208,'Message Filter','Filter','Esquema y elegibilidad')
    card(524,58,208,'Message Filter','Filter','F6 excluye unidades')
    card(778,58,208,'Message Translator','MessageTranslator','Respuesta con citas')
    for x in (224,478,732): f.line([(x,128),(x+46,128)])
    card(16,285,232,'Correlation Identifier','CorrelationIdentifier','UUID común a llamada\ny recibo de auditoría')
    card(373,285,250,'Message Store','MessageStore','Metadatos persistentes\nsin texto documental')
    card(754,285,232,'Message Endpoint','MessageEndpoint','Cliente de plan fijo\nvalida y muestra datos')
    f.line([(120,198),(120,285)]); f.label((120,242),'inicia recibo',17)
    f.line([(248,355),(373,355)]); f.label((311,334),'correlación',17)
    f.line([(881,198),(881,247),(498,247),(498,285)]); f.label((669,247),'resultado y señales',17)
    f.line([(623,355),(754,355)]); f.label((688,333),'tras cierre',17)
    f.text((372,218),'No autorizado  →  denegación',16,'#923D32')
    f.text((624,218),'Señal  →  descarte y traza',16,'#923D32')
    f.save('eip_flujo')


if __name__=='__main__':
    containers(); components(); eip()
