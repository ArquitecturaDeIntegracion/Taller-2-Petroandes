# Ensayo de consolidación y propagación F10

Corrida del 8 de noviembre de 2026, America/Bogota. Docker Desktop con motor
Linux 28.3.2, Python 3.12.16 y Qdrant Client 1.20.0. El perfil `dev` montó el
código local. La imagen `petroandes-educativo:local` se construyó con índice OCI
`sha256:85a345407428977da17b5b04c601fafb0c50c06c961d74b428a78770721c74cf`.

```powershell
docker.exe compose --profile dev build dev
docker.exe compose --profile dev run --rm -T dev tools/f10_check.py --output-dir reports/portable/f10-docker-dev-20261108-184812
```

- La consolidación verificó 19 documentos y publicó 58 fragmentos de 12
  documentos autorizados para el contexto histórico. Confirmó 13 eventos.
  [Consolidación](consolidacion.json) · [Manifiesto](consolidacion-manifiesto.json).
- Una revocación durante la búsqueda provocó abstención. El vector seguía
  presente en Qdrant. La obtención directa y la expansión también se
  denegaron. [Carrera](revocacion-en-consulta.json) · [Vector](vector-revocado.json).
- El fallo antes de activar dejó pendiente el evento. Tras activar y fallar
  antes de confirmar, el reintento reutilizó la generación y confirmó la
  revisión 14 una sola vez. [Fallo](fallo-activacion.json) · [Recuperación](recuperacion.json).
- La copia del PDF modificado quedó sin permiso y el original conservó
  su huella. [Comparación de huellas](huellas-pdf.json).
- Se comparó la colección reconstruida con su referencia. La reversión a la
  misma revisión fue válida. Las generaciones con revisión anterior o
  permisos vencidos se rechazaron. [Reindexación](reindexacion.json) ·
  [Reversión rechazada](rollback-rechazado.json).

Se observaron 126 ms de p95 en cinco consultas calientes, 8 ms en una
revocación durante consulta y 2,61 s en una reaprobación. Son muestras del
contenedor con 14 CPU lógicas y 8,05 GB de memoria visible. La propagación
se ejecutó bajo demanda y las muestras excluyen la revisión humana.
[Resumen de F10](summary.json).

La primera corrida publicó correctamente, pero su comprobación de inventario
agrupó documentos solo por código y omitió versiones del conteo. Se conserva
el [intento inicial](intento-inicial/summary.json). La segunda corrida verificó
las 19 identidades del catálogo. [Guía de reproducción](../../../docs/validacion-dev-f10.md).

La CLI también se probó desde un catálogo vacío con los comandos de la guía
administrativa. F3 extrajo 92 fragmentos. La consolidación confirmó el evento
de revisión 1 y publicó cero fragmentos bajo el contexto habitual. El replay
sin staging devolvió `evento_ya_confirmado`.
[Staging inicial](cli/staging.json) · [Consolidación CLI](cli/consolidacion/summary.json) ·
[Replay CLI](cli/replay-sin-stage.json).

La imagen final se reconstruyó con índice OCI
`sha256:8ccb666e41ad915ae618416aa898df5ef08cad96a5a2ad6043d8f1ddc34b39d4`
y el ensayo volvió a pasar. En la repetición se observaron 229 ms de p95
en cinco consultas calientes, 8 ms en una revocación y 2,52 s en una
reaprobación. [Corrida final](final/summary.json).

El inventario en Docker no informó errores. La suite de regresión aprobó
180 pruebas en 219,92 segundos. [Inventario](preflight/stdout-001.log) ·
[Regresión](pytest/stdout-001.log).
