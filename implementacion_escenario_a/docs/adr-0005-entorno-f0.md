# ADR-0005: entorno reproducible y carga local en Windows

Fecha: 2026-11-01. Estado: decisión técnica implementada y verificada en F0.
No representa revisión académica ni autorización del corpus.

## Contexto

El PATH resuelve Python a un shim de pyenv sin versión seleccionada.
La primera descarga de E5 falló con WinError 1314 al crear un enlace simbólico
en la caché Hugging Face. Los originales y la configuración global se conservan.
F0 exige los modelos y transportes reales, incluyendo una segunda carga offline.

## Decisión

- Crear `.venv` desde Python 3.12.14 disponible y usar su ejecutable explícito.
- Fijar las 75 distribuciones Python mediante un único bloqueo `pip freeze --all`,
  conservado en [requirements.lock](../requirements.lock).
- Usar Sentence Transformers 5.7.0, Transformers 4.57.6, PyTorch 2.15.0,
  qdrant-client 1.20.0, MCP SDK 1.30.0 y laya 0.4.20 según las pruebas reales.
- Materializar modelos bajo `.venv/model-files`, indicando revisión exacta;
  no depender de privilegios para enlaces simbólicos ni activar Developer Mode.
- Mantener E5 `fd1525a9fd15316a2d503bf26ab031a61d056e98`, bundle y pooling de 3.1.
- Fijar laya multilingüe a `e4e9ddf21a7b1903b7acffd8814ad4307bf63a67`,
  revisión incluida en la tabla de pins de laya 0.4.20; CPU, eager, dos hilos.
- Usar Inspector 2.13.0 con su CLI real, stdio y negociación legacy del SDK 1.x.
  Inspector es una herramienta Node separada: su bloqueo pnpm se conserva en ZIP.
  Se configura sesión local de solo lectura y almacén de secretos en memoria.

## Adaptación observada de laya

El cargador oficial `_fix_tokenizer_config` adapta `tokenizer_config.json` para
Transformers 4. Se registran
hashes antes y después en [laya-online.json](../evidence/f0/laya-online.json).
No cambian los pesos, `tokenizer.json` ni el checkpoint seleccionado.
La carga offline debe reproducir los hashes efectivos y los cuatro juicios.
Este registro documenta la adaptación de compatibilidad; no sustituye al evaluador.

## Alternativas consideradas

Modificar pyenv global o permisos de Windows agregaría cambios fuera del proyecto.
Cambiar embeddings, checkpoint o evaluador rompería el contrato sin resolver el
problema de almacenamiento de archivos. Mantener enlaces simbólicos dejó un fallo
real; se adoptaron archivos materializados. No se añadió ningún servicio remoto.

## Consecuencias

Los pesos y dependencias ocupan espacio local y se omiten de Git bajo `.venv`.
Las fuentes, sondas, bloqueos y evidencias quedan conservados y las descargas
iniciales requieren red; la inferencia de consulta y evaluación es local.
Los tiempos observados son ensayos mínimos, sin garantía de latencia productiva.
La calibración de laya y los esperados del corpus siguen requiriendo revisión.

Referencias primarias consultadas:
[E5](https://huggingface.co/intfloat/multilingual-e5-small),
[laya](https://github.com/NandhaKishorM/laya),
[Inspector](https://modelcontextprotocol.io/docs/tools/inspector).
