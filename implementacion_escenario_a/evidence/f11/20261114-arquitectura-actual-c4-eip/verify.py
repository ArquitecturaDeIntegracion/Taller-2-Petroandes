"""Registra la revisión del documento completo sin ejecutar ataques ni reserva."""
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile
from pypdf import PdfReader

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
APP=ROOT/'implementacion_escenario_a'
OUT=ROOT/'output/doc/Arquitectura_Actual_PetroAndes_C4_EIP_F9_2.docx'
EVIDENCE=APP/'evidence/f11/20261114-arquitectura-actual-c4-eip'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=PdfReader(BASE/'documento.pdf')
assert len(reader.pages)==4
assert len(list((BASE/'paginas').glob('page-*.png')))==4
with ZipFile(OUT) as archive:
    media=[name for name in archive.namelist() if name.startswith('word/media/')]
    assert len(media)==4
    rels=ET.fromstring(archive.read('word/_rels/document.xml.rels'))
    local=[x.get('Target') for x in rels if x.get('TargetMode')=='External' and x.get('Target','').startswith('../')]
    assert len(local)==4 and all((OUT.parent/name).resolve().is_file() for name in local)
    document=ET.fromstring(archive.read('word/document.xml'))
    pictures=document.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr')
    assert len(pictures)==4 and all(p.get('descr') for p in pictures)
    styles=ET.fromstring(archive.read('word/styles.xml'))
    assert not styles.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pBdr')
manifest=APP/'evidence/f9/20261114-arnes-contenido/fuentes.jsonl'
registered=[json.loads(line) for line in manifest.read_text().splitlines()]
code=[r for r in registered if r['base']=='app' and (r['path'].endswith('.py') or r['path']=='compose.yaml')]
assert all(digest(APP/r['path'])==r['sha256'] for r in code)
f9=json.loads((APP/'evidence/f9/20261114-arnes-contenido/summary.json').read_text())
assert f9['status']=='passed' and f9['regresion_docker_dev']['pruebas_aprobadas']==255
demo=json.loads((APP/'config/mcp-demo.json').read_text())
assert demo['revision']==15
bundle=json.loads((APP/'config/embedding-bundle.json').read_text())
assert bundle['dimension']==384 and bundle['max_input_tokens']==448
EVIDENCE.mkdir(parents=True,exist_ok=False)
for name in ('c4_contexto.png','c4_contenedores.png','c4_componentes.png','eip_integracion.png',
             'diagrams.py','build.py','render.ps1','rasterize.py','verify.py'):
    assert not name.endswith('.py') or len((BASE/name).read_text(encoding='utf-8').splitlines())<=200
    shutil.copyfile(BASE/name,EVIDENCE/name)
shutil.copyfile(BASE/'documento.pdf',EVIDENCE/'revision-visual.pdf')
qa=[{'pagina':i,'palabras_texto':len(page.extract_text().split()),
    'png_sha256':digest(BASE/f'paginas/page-{i}.png'),'qa':'inspeccionada_sin_recortes_ni_solapamientos'}
    for i,page in enumerate(reader.pages,1)]
(EVIDENCE/'paginas.json').write_text(json.dumps(qa,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
summary={'status':'passed','fecha_utc':datetime.now(timezone.utc).isoformat(),
    'documento':{'base':'project','path':OUT.relative_to(ROOT).as_posix(),'sha256':digest(OUT)},
    'alcance':'arquitectura completa y funcionamiento del Escenario A con mejoras F9.2',
    'paginas':4,'diagramas':{'C4_contexto':1,'C4_contenedores':1,'C4_componentes':1,'EIP_integracion':1},
    'render':'Microsoft Word a PDF y rasterizador render_docx.py de documents',
    'qa_visual':'cuatro paginas finales inspeccionadas','enlaces_locales_verificados':len(local),
    'diagramas_con_texto_alternativo':len(pictures),'archivos_implementacion_con_hash_coincidente':len(code),
    'pruebas_docker':'evidencia F9.2 previa verificada; sin nueva corrida documental',
    'reserva_ejecutada':False,'copilot_adversarial':'no_evaluado',
    'notacion':[{'autor':'Simon Brown','url':'https://c4model.com/','licencia':'CC BY 4.0'},
        {'autor':'Gregor Hohpe y Bobby Woolf','url':'https://www.enterpriseintegrationpatterns.com/patterns/messaging/','licencia':'CC BY 4.0'}]}
(EVIDENCE/'summary.json').write_text(json.dumps(summary,ensure_ascii=True,indent=2)+'\n',encoding='utf-8')
source_names=['docs/adr-0013-mcp-demostracion-unica.md','docs/adr-0015-arnes-f9-2.md',
    'docs/f10-operacion.md','docs/validacion-dev-f8.md','config/embedding-bundle.json','config/mcp-demo.json',
    'config/demo-pruebas.json','petroandes/index/publication.py','petroandes/retrieve/service.py',
    'evidence/f9/20261114-arnes-contenido/summary.json','evidence/f8/20261108/summary.json']
sources=[{'base':'app','path':name,'sha256':digest(APP/name)} for name in source_names]
sources.extend({'base':'app','path':r['path'],'sha256':r['sha256']} for r in code)
sources.extend({'base':'project','path':p.relative_to(ROOT).as_posix(),'sha256':digest(p)}
    for p in (BASE/'build.py',BASE/'diagrams.py',BASE.parent/'f9_2_documento/build.py',BASE.parent/'f9_2_documento/figures.py'))
(EVIDENCE/'fuentes.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=True)+'\n' for r in sources),encoding='utf-8')
assets=BASE.parent/'eip_petroandes_qa/assets'
icons=[r for r in json.loads((assets/'sources.json').read_text())
       if r.get('local') in {'ChannelAdapter.gif','Sequencer.gif','DataEnricher.gif','MessageStore.gif','Aggregator.gif','Filter.gif'}]
assert all(digest(assets/r['local'])==r['sha256'] for r in icons)
(EVIDENCE/'iconos-eip.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=True)+'\n' for r in icons),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True))
