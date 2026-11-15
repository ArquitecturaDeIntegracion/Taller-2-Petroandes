"""Rasterizador oficial con exportación nativa Word ante ausencia de LibreOffice."""
import importlib.util
import os
from pathlib import Path
from pypdf import PdfReader

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
runtime=Path(os.__file__).resolve().parents[1]
poppler=runtime.parent/'native/poppler/Library/bin'
if not poppler.exists():
    poppler=Path('C:/Users/jcjca/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin')
os.environ['PATH']=str(poppler)+os.pathsep+os.environ['PATH']
script=Path('C:/Users/jcjca/.codex/plugins/cache/openai-primary-runtime/documents/26.1111.10930/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('render_docx',script)
renderer=importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)
renderer.convert_to_pdf=lambda *a,**kw:(str(BASE/'documento.pdf'),'Exportación Microsoft Word; sin LibreOffice instalado')
renderer.rasterize(str(ROOT/'output/doc/Diagrama_Integral_EIP_PetroAndes_Actual.docx'),str(BASE/'paginas'),150,False,False)
reader=PdfReader(BASE/'documento.pdf')
print('Páginas:',len(reader.pages))
for i,page in enumerate(reader.pages,1):
    print(i,len(page.extract_text().split()),page.extract_text()[:90].replace('\n',' '))
