"""Descarga únicamente arte gráfico público para el documento, sin instalar paquetes."""
from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import json,hashlib
BASE=Path(__file__).resolve().parent
OUT=BASE/'icons'; OUT.mkdir(parents=True,exist_ok=True)
DEV='https://raw.githubusercontent.com/devicons/devicon/master/icons/'
SIMPLE='https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/'
items={
 'python':DEV+'python/python-original.svg','docker':DEV+'docker/docker-original.svg',
 'sqlite':DEV+'sqlite/sqlite-original.svg','vscode':DEV+'vscode/vscode-original.svg',
 'pytorch':DEV+'pytorch/pytorch-original.svg','nodejs':DEV+'nodejs/nodejs-original.svg',
 'linux':DEV+'linux/linux-original.svg','powershell':DEV+'powershell/powershell-original.svg',
 'qdrant':SIMPLE+'qdrant.svg','mcp':SIMPLE+'modelcontextprotocol.svg',
 'huggingface':SIMPLE+'huggingface.svg','pydantic':SIMPLE+'pydantic.svg',
 'pytest':DEV+'pytest/pytest-original.svg'}
def get(item):
 name,url=item
 try:
  raw=urlopen(Request(url,headers={'User-Agent':'PetroAndes-documentation'}),timeout=30).read()
  assert b'<svg' in raw
  (OUT/(name+'.svg')).write_bytes(raw)
  return {'name':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'status':'ok'}
 except Exception as exc:return {'name':name,'url':url,'status':'error','error':str(exc)}
rows=list(ThreadPoolExecutor(max_workers=6).map(get,items.items()))
(BASE/'icon_sources.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
for r in rows:print(r['name'],r['status'])
