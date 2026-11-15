"""Vistas del sistema actual; C4 separa contexto, contenedores y componentes."""
import sys
from pathlib import Path
from PIL import Image

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parent/'f9_2_documento'))
from figures import Figure as Canvas, GRAY, INK, ASSETS, S


class Figure(Canvas):
    def save(self,name): self.im.save(BASE/(name+'.png'),dpi=(400,400))


def context():
    f=Figure(340)
    f.node(20,52,200,100,'Consultante','[Persona]','Pregunta y revisa citas',gray=True)
    f.node(20,220,200,100,'Revisor del grupo','[Persona]','Autoriza por evidencia',gray=True)
    f.node(319,54,280,110,'Clientes de consulta','[Sistemas externos]','Inspector y VS Code',gray=True)
    f.node(679,141,299,122,'PetroAndes','[Sistema en alcance]','Evidencia con permisos')
    f.line([(220,102),(319,102)]); f.label((269,83),'consulta',17)
    f.line([(599,108),(638,108),(638,177),(679,177)]); f.label((641,127),'pregunta',17)
    f.line([(679,229),(638,229),(638,279),(459,279),(459,164)]); f.label((561,279),'extractos o abstención',17)
    f.line([(220,270),(280,270),(280,309),(828,309),(828,263)]); f.label((552,309),'registra y revisa decisiones',17)
    f.text((500,17),'C4 nivel 1  ·  Contexto del Escenario A',20,bold=True)
    f.save('c4_contexto')


def containers():
    f=Figure(485)
    f.rect((178,15,984,457),'#FCFDFE','#8A9CA9',3)
    f.text((195,33),'PetroAndes  ·  aplicaciones y almacenes',18,bold=True,anchor='la')
    f.node(205,65,215,100,'Fuentes y pesos','[Archivos locales]','PDF y modelo E5',store=True)
    f.node(478,65,220,100,'CLI de operación','[Aplicación Python]','Ingesta y publicación')
    f.node(751,65,205,100,'Gobierno','[SQLite]','Decisiones y outbox',store=True)
    f.node(15,240,135,100,'Clientes MCP','[Cliente externo]','Inspector y IDE',gray=True)
    f.node(478,240,220,100,'Servidor petroandes','[Aplicación Python]','Consulta gobernada')
    f.node(751,240,205,100,'Proyecciones','[Qdrant y SQLite]','Vectores y términos',store=True)
    f.node(205,352,215,100,'Cliente restringido','[Aplicación Python]','Plan fijo sin LLM')
    f.node(751,352,205,100,'Recibos y reportes','[Archivos JSON]','Trazas y validación',store=True)
    f.line([(420,115),(478,115)]); f.label((449,96),'lee',17)
    f.line([(698,115),(751,115)]); f.label((725,96),'registra',16)
    f.line([(588,165),(588,205),(853,205),(853,240)]); f.label((633,205),'publica',16)
    f.line([(150,285),(478,285)]); f.label((313,265),'JSON RPC por stdio',17)
    f.line([(698,268),(725,268),(725,146),(751,146)]); f.label((724,180),'autoriza',16)
    f.line([(698,310),(751,310)]); f.label((725,291),'lee',16)
    f.line([(420,402),(448,402),(448,323),(478,323)]); f.label((443,365),'stdio',16)
    f.line([(676,340),(676,403),(751,403)]); f.label((674,372),'persiste',16)
    f.text((500,474),'Azul  aplicación    ·    Azul claro  almacén    ·    Gris  cliente externo',17,GRAY)
    f.save('c4_contenedores')


def components():
    f=Figure(425)
    f.rect((185,16,984,400),'#FCFDFE','#8A9CA9',3)
    f.text((200,34),'Servidor petroandes  ·  componentes de consulta',18,bold=True,anchor='la')
    f.node(14,180,145,104,'Cliente MCP','[Aplicación]','Plan o pregunta',gray=True)
    f.node(215,80,220,102,'Entrada MCP','[mcp_tools.py]','Valida contratos')
    f.node(473,80,220,102,'Recuperador','[retrieve/]','E5 y BM25 con RRF')
    f.node(731,80,220,102,'Compositor F6','[compose/]','Extractos con citas')
    f.node(215,278,220,102,'Auditoría F9.2','[security/audit.py]','Inicio y cierre durable')
    f.node(473,278,220,102,'Elegibilidad','[governance/]','Objeto y vigencia')
    f.node(731,278,220,102,'Detector F9.2','[security/detection.py]','Texto y señales PDF')
    f.line([(159,209),(185,209),(185,130),(215,130)]); f.label((184,166),'llama',16)
    f.line([(435,130),(473,130)]); f.label((454,110),'delega',15)
    f.line([(693,130),(731,130)]); f.label((712,110),'buscar',15)
    f.line([(325,182),(325,278)]); f.label((325,229),'antes de devolver',16)
    f.line([(583,182),(583,278)]); f.label((583,229),'prefiltra y revalida',16)
    f.line([(841,182),(841,278)]); f.label((841,229),'excluye señales',16)
    f.line([(215,161),(173,161),(173,251),(159,251)])
    f.text((87,307),'respuesta',16,GRAY)
    f.text((500,413),'Flechas  invocaciones    ·    obtener_fragmento conserva lectura literal autorizada',16,GRAY)
    f.save('c4_componentes')


def integration():
    f=Figure(440)
    f.text((500,18),'Pipes and Filters  ·  preparación documental y consulta síncrona',19,bold=True)
    def card(x,y,title,icon,detail):
        f.rect((x,y,x+210,y+140),'#FCFDFE','#A8BAC8')
        img=Image.open(ASSETS/(icon+'.gif')).convert('RGBA')
        ratio=min(104*S/img.width,47*S/img.height)
        img=img.resize((int(img.width*ratio),int(img.height*ratio)),Image.Resampling.NEAREST)
        f.im.paste(img,(int((x+105)*S-img.width/2),int((y+8)*S)),img)
        f.text((x+105,y+79),title,19,bold=True)
        f.text((x+105,y+113),detail,17)
    first=[('Channel Adapter','ChannelAdapter','PDF a texto trazable'),('Splitter','Sequencer','Secciones y fragmentos'),
           ('Content Enricher','DataEnricher','Contexto y señales'),('Message Store','MessageStore','Staging y proyecciones')]
    second=[('Channel Adapter','ChannelAdapter','MCP con JSON Schema'),('Message Filter','Filter','Elegibilidad documental'),
            ('Aggregator','Aggregator','RRF de E5 y BM25'),('Message Filter','Filter','F6 y suficiencia')]
    for y,items in ((51,first),(270,second)):
        for x,args in zip((15,268,521,774),items): card(x,y,*args)
        for x in (225,478,731): f.line([(x,y+70),(x+43,y+70)])
    f.line([(879,191),(879,228),(626,228),(626,270)]); f.label((751,228),'recupera candidatos',16)
    f.text((328,228),'Consulta  →',18,GRAY,bold=True)
    f.text((500,431),'Salida  extractos o abstención  +  recibo correlacionado obligatorio antes de responder',17,GRAY)
    f.save('eip_integracion')


if __name__=='__main__':
    context(); containers(); components(); integration()
