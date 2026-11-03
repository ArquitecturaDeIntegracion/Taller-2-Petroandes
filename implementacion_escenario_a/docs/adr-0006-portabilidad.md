# ADR-0006: raíces portables y entornos reproducibles

Fecha: 2026-11-01. Estado: adoptada; ejecución Docker Linux comprobada.

## Problema y alcance

Las evidencias originales contenían ubicaciones absolutas y el cierre F0 consumía
la ruta histórica de modelos. El lock de Windows incluía pywin32 incondicional.
Esto dificultaba mover el taller y preparar una instalación Linux.
El cambio prepara la continuación educativa de F1/F2; no completa el servicio 3.2.

## Decisión

- La raíz del repositorio contiene todo el taller; `implementacion_escenario_a`
  es la raíz de aplicación. Conservar documentos, corpus y fuentes registradas.
- `petroandes/paths.py` deriva las raíces desde el archivo y admite overrides
  `PETROANDES_*`. Los relativos se interpretan desde la aplicación, no desde cwd.
- Persistir referencias POSIX con base explícita; rechazar absolutas y escapes
  al resolver referencias de datos. Resolver absolutas únicamente en ejecución.
- Guardar modelos y caché fuera de `.venv`; migrar con hashes y sin sobrescribir.
- Preservar evidencia F0/F1 y `requirements.lock` originales. Leer referencias
  históricas mediante revisión de modelo; generar nuevos informes con esquema 2.
- El lock portable añade un marcador de plataforma para pywin32. El lock de
  desarrollo incorpora debugpy. No se comparte el entorno virtual.
- Instalar el paquete editable mediante pyproject; depurar con perfiles VS Code.
- Docker usa contexto del taller, Python 3.12, PyTorch CPU, Node 22 e Inspector;
  cachés y artefactos persistentes se separan del código.

## Alternativas consideradas

Sustituir texto absoluto en toda evidencia alteraría su procedencia: se descarta.
Depender de cwd haría frágiles los comandos externos y el debugger: se descarta.
Copiar `.venv` entre sistemas no reproduce binarios compatibles: se recrea.
Se mantiene el lock histórico y se deriva otro para no invalidar su cierre F0.

## Validaciones y límites

Las pruebas locales verifican contratos, cambios de cwd, copia de código a una ruta
con espacios/acentos, referencias históricas y el marcador Linux de pywin32.
Se comprobaron modelos reales offline tras migrarlos, Inspector y un breakpoint
real con debugpy. Los resultados detallados están en el resumen y el estado.

El primer intento falló por ausencia del motor, tras un error `dockerInference`.
Al abrir Docker Desktop se construyó la imagen y pasaron 19 comprobaciones reales:
pruebas, almacenamiento, corpus, MCP, breakpoint y modelos offline. Ver la
[validación Docker](docker-validacion.md). Se añadió `dev` con el código local
montado en lectura, más volúmenes de escritura para caché, artefactos e informes.
No se reinicializaron volúmenes ni la configuración global de Docker.

## Consecuencias

Las ubicaciones absolutas observadas en evidencia antigua siguen siendo históricas.
Los marcadores nuevos representan raíces, no cadenas ejecutables por sí solas.
La copia del proyecto requiere también sus fuentes del taller. Los locks fijan
paquetes Python; las imágenes base conservan actualizaciones de sus etiquetas.
La reproducción limpia completa sigue siendo una comprobación futura de F11.
