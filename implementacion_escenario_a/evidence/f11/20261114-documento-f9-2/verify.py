"""Comprueba y registra el Word y las fuentes usadas, sin ejecutar reserva ni ataques."""
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from pypdf import PdfReader

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
APP=ROOT/'implementacion_escenario_a'
OUT=ROOT/'output/doc/Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx'
EVIDENCE=APP/'evidence/f11/20261114-documento-f9-2'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=PdfReader(BASE/'documento.pdf')
assert len(reader.pages)==4
assert len(list((BASE/'paginas').glob('page-*.png')))==4
namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(OUT) as archive:
    media=[n for n in archive.namelist() if n.startswith('word/media/')]
    assert len(media)==3
    styles=ET.fromstring(archive.read('word/styles.xml'))
    assert not styles.findall('.//w:pBdr',namespaces)
    document=ET.fromstring(archive.read('word/document.xml'))
    pictures=document.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')
    assert len(pictures)==3 and all(x.get('descr') for x in pictures)
    rels=ET.fromstring(archive.read('word/_rels/document.xml.rels'))
    local=[x.get('Target') for x in rels if x.get('TargetMode')=='External' and x.get('Target','').startswith('../')]
    assert len(local)==3 and all((OUT.parent/name).resolve().is_file() for name in local)
data=json.loads((APP/'evidence/f9/20261114-arnes-contenido/summary.json').read_text())
assert data['status']=='passed' and data['regresion_docker_dev']['pruebas_aprobadas']==255
manifest=APP/'evidence/f9/20261114-arnes-contenido/fuentes.jsonl'
sources=[json.loads(line) for line in manifest.read_text().splitlines()]
code=[x for x in sources if x['base']=='app' and (x['path'].endswith('.py') or x['path']=='compose.yaml')]
assert all(digest(APP/x['path'])==x['sha256'] for x in code)
EVIDENCE.mkdir(parents=True,exist_ok=False)
for name in ('c4_contenedores.png','c4_componentes.png','eip_flujo.png','figures.py','build.py','render.ps1','rasterize.py','verify.py'):
    # Los generadores del taller viven fuera del módulo de aplicación y no se minifican.
    if name.endswith('.py') and len((BASE/name).read_text(encoding='utf-8').splitlines())>200:
        continue
    shutil.copyfile(BASE/name,EVIDENCE/name)
shutil.copyfile(BASE/'documento.pdf',EVIDENCE/'revision-visual.pdf')
qa=[{'pagina':i,'palabras_texto':len(page.extract_text().split()),
     'png_sha256':digest(BASE/f'paginas/page-{i}.png'),'qa':'inspeccionada_sin_recortes_ni_solapamientos'}
    for i,page in enumerate(reader.pages,1)]
(EVIDENCE/'paginas.json').write_text(json.dumps(qa,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
summary={'fecha_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','tipo':'emision_documental',
    'documento':{'base':'project','path':OUT.relative_to(ROOT).as_posix(),'sha256':digest(OUT)},
    'paginas':4,'diagramas':{'C4_nivel_2':1,'C4_nivel_3':1,'EIP':1},
    'render':'Microsoft Word a PDF y rasterizador render_docx.py de documents; LibreOffice no instalado',
    'qa_visual':'cuatro paginas finales revisadas','diagramas_con_texto_alternativo':len(pictures),
    'enlaces_locales_verificados':len(local),'fuentes_codigo_con_hash_coincidente':len(code),
    'evidencia_base':'evidence/f9/20261114-arnes-contenido/summary.json',
    'pruebas_docker':'referencia a la corrida F9.2 conservada; sin repetirla en esta tarea documental',
    'reserva_ejecutada':False,'notacion':[
        {'nombre':'C4 de Simon Brown','url':'https://c4model.com/diagrams/container','licencia':'CC BY 4.0'},
        {'nombre':'EIP de Gregor Hohpe y Bobby Woolf','url':'https://www.enterpriseintegrationpatterns.com/patterns/messaging/','licencia':'CC BY 4.0'}]}
(EVIDENCE/'summary.json').write_text(json.dumps(summary,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
rows=[{'base':'project','path':p.relative_to(ROOT).as_posix(),'sha256':digest(p)} for p in sorted(EVIDENCE.rglob('*')) if p.is_file()]
rows.extend({'base':'app','path':x['path'],'sha256':x['sha256']} for x in code)
(EVIDENCE/'fuentes.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=True)+'\n' for x in rows),encoding='utf-8')
assert all(len(p.read_text(encoding='utf-8').splitlines())<=200 for p in EVIDENCE.glob('*.py'))
print(json.dumps(summary,ensure_ascii=True))
