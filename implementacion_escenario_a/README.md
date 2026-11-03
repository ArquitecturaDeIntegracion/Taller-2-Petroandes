# PetroAndes: implementación educativa del Escenario A

Python, Qdrant y módulos pequeños para la parte 3.2 de ARTI 4212.
F0 se comprobó en Windows y Docker; F1 tiene contratos iniciales, F2 tiene catálogos
y gobierno; F3 prepara PDF y F4 publica índices gobernados, validados en `dev`.
Consulta [estado](docs/estado.md), [F3](docs/f3-ingesta.md) y [F4](docs/f4-indices.md).
Laboratorio: [doce certificaciones simuladas registradas](docs/certificacion-laboratorio-20261103.md).

## Qué copiar o subir al repositorio

Conserva **todo el taller** y su relación de carpetas:

```text
raiz-del-repositorio/
  Contenido de la Actividad.docx
  ARTI4212_Caso_PetroAndes.pdf
  ARTI4212_Caso_PetroAndes.md
  contexto_arquitectura_integracion.md
  plan_trabajo_alternativa_1_escenario_a.md
  corpus/
  output/doc/
  implementacion_escenario_a/       # raíz de la aplicación
```

Las fuentes exactas están en `knowledge/sources.json`. No basta con copiar esta
subcarpeta: las herramientas comprueban fuentes y hashes en la raíz del taller.
No compartas `.venv`, `.cache`, `.env`, `artifacts` ni informes locales nuevos.
Los `.gitignore` separan esos archivos de fuentes, contratos y evidencia histórica.

## Instalación local

Requisitos: Python **3.12**, Node **>=22.19**, npm y VS Code con las extensiones
Python y Python Debugger. Node/Inspector solo se necesitan para las pruebas MCP.
Abre `implementacion_escenario_a/` en VS Code. Los siguientes comandos parten de
esta carpeta; no contienen rutas del equipo original.

Windows, PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
node --version
npm install --prefix .cache/inspector --save-exact @modelcontextprotocol/inspector@2.13.0
```

Linux/macOS, bash:

```bash
python3.12 -m venv .venv
# En Linux, instalar primero la distribución CPU de PyTorch:
.venv/bin/python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
node --version
npm install --prefix .cache/inspector --save-exact @modelcontextprotocol/inspector@2.13.0
```

En macOS omite el índice CPU de Linux; ese sistema no se ha validado.
Linux x86-64 se comprobó mediante la imagen Docker descrita más adelante.
`requirements.lock` conserva la evidencia original de F0. Las instalaciones nuevas
usan `requirements-portable.lock` y `requirements-dev.lock` (incluye debugpy).
`pywin32` se instala solo en Windows. Nunca copies `.venv` entre equipos o sistemas.

En el entorno F0 anterior ya se trasladaron los modelos sin cambiar sus hashes.
Para otro entorno que aún tenga `.venv/model-files`, ejecuta una sola vez:

```powershell
.\.venv\Scripts\python.exe tools/migrate_models.py --apply
```

El destino es `.cache/models`; la herramienta rechaza sobrescrituras.

## Ejecutar y verificar localmente

En PowerShell define un alias de sesión para el intérprete del proyecto:

```powershell
Set-Alias python .\.venv\Scripts\python.exe
python -m pip check
python tools/preflight.py
python tools/validate_agent.py
python -m pytest -q -p no:cacheprovider --basetemp artifacts/pytest-local
python tools/check_portability.py --output reports/portable/relocation-local.json
python tools/read_source.py plan --section "F2 Gobierno"
```

En bash usa `.venv/bin/python` en lugar de `python`, o activa el entorno con
`source .venv/bin/activate`. La instalación editable permite importar `petroandes`.
Las herramientas localizan las raíces por su ubicación, aunque el cwd sea distinto.
`check_portability.py` copia el taller a otra ruta y reutiliza el intérprete actual.

Sondas reales del entorno (crean informes; no implementan la aplicación completa):

```powershell
python tools/f0.py storage --output reports/portable/storage-local.json
python tools/f0.py e5 --output reports/portable/e5-local.json
python tools/f0.py laya --output reports/portable/laya-local.json
python tools/f0_mcp.py --output-dir reports/portable/mcp-local
python tools/check_f0.py --output reports/portable/closure-local.json
```

La primera carga E5/laya descarga los modelos y requiere conexión y espacio libre.
Después repite con `--offline` y otro nombre de informe para comprobar la caché.
Inspector requiere Node y su instalación npm. Para conservar corridas, usa destinos
nuevos; algunas herramientas rechazan directorios existentes.
`check_f0.py` revalida evidencia histórica y pesos disponibles; no acredita por sí
solo una instalación nueva ni sustituye ejecutar las sondas en ella.

## Depuración local en VS Code

1. Selecciona el intérprete `.venv` con **Python: Select Interpreter**.
2. Pon un breakpoint en `tools/preflight.py`, en la carga del registro de fuentes.
3. En **Ejecutar y depurar**, elige **PetroAndes: inventario local** y pulsa F5.
4. Usa **PetroAndes: pruebas** para depurar pytest.

Hay una comprobación automatizada del adaptador y de un breakpoint real:

```powershell
python tools/debug_smoke.py --output reports/portable/debug-local.json
```

Estos perfiles ejecutan herramientas existentes; no hay aún una API final que iniciar.

## Docker y depuración en contenedor

Requisitos: Docker Desktop con motor **Linux** iniciado, o Docker Engine Linux
con Compose v2. Ejecuta desde esta carpeta:

```powershell
mkdir reports/portable -Force
docker compose config --quiet
docker compose build project
docker compose run --rm project tools/preflight.py
docker compose run --rm project tools/validate_agent.py
docker compose run --rm project -m pytest -q -p no:cacheprovider --basetemp artifacts/pytest-docker
docker compose run --rm project tools/f0.py storage --output reports/portable/storage-docker.json
docker compose run --rm project tools/f0.py e5 --output reports/portable/e5-docker.json
docker compose run --rm project tools/f0.py laya --output reports/portable/laya-docker.json
docker compose run --rm project tools/f0_mcp.py --output-dir reports/portable/mcp-docker
```

En bash, crea el directorio con `mkdir -p reports/portable`.
El contexto de construcción es la raíz del taller, definido en `compose.yaml`.
La imagen incluye fuentes, Python, PyTorch CPU, Node e Inspector. Excluye entornos,
cachés y archivos privados locales mediante `Dockerfile.dockerignore`.
Los modelos/cachés y artefactos usan volúmenes; `reports/portable` se comparte
con el host. La primera inferencia descarga modelos dentro del volumen Docker.
No monta ni reutiliza el entorno virtual de Windows.

Para F2, el perfil `dev` refleja el código local sin reconstruir por cada edición:

```powershell
docker compose --profile dev run --rm dev tools/read_source.py plan --section "F2 Gobierno"
docker compose --profile dev run --rm dev -m pytest -q -p no:cacheprovider --basetemp artifacts/pytest-f2
```

Guarda los datos generados en `artifacts/`. Reconstruye si cambian dependencias.

Para depurar código local dentro del contenedor:

```powershell
docker compose --profile debug up debug
```

El proceso espera al depurador. Elige **PetroAndes: adjuntar Docker** en VS Code y
pulsa F5. El puerto 5678 se publica únicamente en localhost; los mapeos traducen
la ruta del contenedor al proyecto. El código está montado en lectura; caché,
artefactos e informes tienen sus propios montajes de escritura.
Termina con Ctrl+C y `docker compose --profile debug down`.
No uses `down -v` si quieres conservar los modelos descargados.

**Validado en Linux x86-64:** imagen construida, 36 pruebas en imagen y en `dev`,
SQLite/Qdrant, corpus, MCP, breakpoint y E5/laya offline. El bloqueo anterior del
motor está resuelto. Consulta [resultados y batería repetible](docs/docker-validacion.md).

## Rutas, agente y continuidad

`petroandes/paths.py` define las raíces. Las referencias persistidas usan `/`, una
base explícita y rutas relativas. `.env.example` enumera ajustes opcionales
`PETROANDES_*`; Python **no carga `.env` automáticamente**: exporta las variables
en tu terminal. Los overrides relativos se resuelven desde la aplicación.
En Docker, configura variables en Compose; evita exportar rutas Windows al contenedor.

Las evidencias anteriores permanecen intactas. Las nuevas usan esquema 2 y
marcadores como `${APP_ROOT}`; son referencias documentadas, no comandos literales.

Para continuar con Codex abre esta carpeta, crea un chat y usa [INICIO.md](INICIO.md).
`AGENTS.md` exige rutas portables y máximo 200 líneas por archivo textual.
Las habilidades nativas están en `.agents/skills`. `config.json` es informativo;
la configuración del cliente está en `.codex/config.toml` y no impone un modelo.

Consulta el [resumen ejecutivo](docs/resumen-portabilidad.md), la
[decisión de portabilidad](docs/adr-0006-portabilidad.md) y el
[estado para continuar el plan](docs/estado.md).
