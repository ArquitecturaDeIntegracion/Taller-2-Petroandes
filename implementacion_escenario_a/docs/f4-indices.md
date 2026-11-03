# F4: embeddings y publicación gobernada en Docker dev

Fecha: 2026-11-01. Implementación técnica educativa; revisión académica pendiente.

## Implementación

`embeddings/encoder.py` comprueba los nueve artefactos E5 fijados desde F0,
tokenización completa, prefijos, dimensión, valores finitos y L2. Registra versiones
reales y fingerprint del bundle efectivo. La comparación con pooling manual usa
el modelo real, máscara de atención, promedio y normalización.
Configuración: `config/embedding-bundle.json` y `config/e5-artifacts.json`.

`index/stage.py` verifica manifiesto/JSONL/SQLite de F3, hash de los PDF y los inputs
exactos. `index/dense.py` posee Qdrant local y registra identidad/hash, generación,
revisión y fingerprint. Su adaptador rechaza bundles distintos aun con dimensión 384.

`index/projections.py` conserva fragmentos/padres autorizados y tokens léxicos en
SQLite. Mantiene códigos completos con guiones y versiones; BM25 se construye
solo sobre los IDs elegibles suministrados. F5 añadirá recuperación híbrida y RRF.

`index/generation.py`, `publication.py` y `registry.py` preparan ambas ramas,
verifican hashes, IDs, payloads y metadatos, y activan el puntero transaccionalmente.
La barrera SQLite de gobierno impide cambios concurrentes durante la activación;
se vuelve a evaluar el período después de verificar archivos. El lector de
snapshots respeta transacciones externas. [ADR-0008](adr-0008-publicacion-f4.md).

Los metadatos publicados identifican la revisión actual; el gobierno observado
en F3 queda rotulado como procedencia de ingesta. Ningún payload concede permisos.
Las consultas futuras deben volver al registro; no basta con abrir el índice.

## Resultado observado

Auditoría separada de los **92 fragmentos** F3 baseline, sin colección consultable:

| Medida | Resultado real en Docker dev |
| --- | --- |
| Vectores | 92 × 384, todos finitos |
| Norma L2 mínima / máxima | 0,9999999404 / 1,0000001192 |
| CPU / lote | dos hilos Torch / cuatro entradas |
| Lotes | 23 |
| Inferencia acumulada de lotes | 8,727 s |
| Generación y guardado de auditoría | 8,898 s |
| Carga y comprobación inicial del modelo | 3,479 s |
| RSS máximo de las muestras al terminar cada lote | 1229,633 MiB |
| Diferencia máxima frente a pooling manual | 6,5193 × 10⁻⁸ |

RSS muestreado no equivale a un pico continuo. No se establece un SLO ni se
generalizan estas medidas a otra máquina. NPY se relee sin pickle y se compara
exactamente con los vectores generados; cada fila enlaza UUID y hash del input.

Los perfiles baseline y laboratorio conservan **19 documentos, cuatro excluidos,
quince pendientes, cero certificados y revisión 1**. El contexto local explícito
está en `config/f4-context.json`; no registra decisiones ni amplía permisos.
Ambas generaciones publicadas tienen **cero fragmentos y cero puntos** por la
elegibilidad actual. El inventario F3 y la auditoría siguen completos.

| Perfil | Generación activa |
| --- | --- |
| baseline | `1589c208-0450-5b25-b58c-d61373aa340d` |
| laboratorio | `15ca08a0-c114-548d-8aaf-249e24211178` |

Las pruebas positivas usan documentos y decisiones ficticios en directorios
temporales. Verifican E5 y Qdrant reales, publicación no vacía, filtros, reapertura
en otro proceso, idempotencia, dueño único, cambio de hash, revocación, vencimiento,
carreras, rollback del puntero y alteraciones de vectores/payloads/SQLite/manifiesto.
No usan esperados del corpus ni las propuestas de reserva académica.
La regresión final aprobó **134 pruebas** en Docker `dev`, sin advertencias.

## Reproducción

Desde esta carpeta, el perfil `dev` monta código local y conserva volúmenes de
modelos/artefactos. Cada orden usa el entrypoint Python existente de la imagen.
No requiere reconstrucción porque no cambiaron dependencias.

```powershell
docker compose --profile dev run --rm dev tools/validate_agent.py
docker compose --profile dev run --rm dev tools/preflight.py
docker compose --profile dev run --rm dev tools/read_source.py plan --section "F4 "
docker compose --profile dev run --rm dev -m pytest -q -p no:cacheprovider
docker compose --profile dev run --rm dev tools/f4.py --help
```

`tools/f4.py audit --stage MANIFEST_F3 --output DIRECTORIO_NUEVO` genera auditoría.
`publish --profile PERFIL --stage MANIFEST_F3 --output RESULTADO_JSON` publica
solamente elegibles; `inspect --profile PERFIL --output RESULTADO_JSON` reabre y
verifica la generación activa. Ante corrupción o revisión distinta falla cerrado.
Los comandos exactos usados quedan en los recibos de evidencia enlazados abajo.

Ejecutar estos procesos por turnos sobre cada perfil. No abrir Qdrant local desde
CLI y servidor simultáneamente. Para recuperar, reconstruir desde PDF/gobierno;
no usar snapshots nativos. Se conservan colecciones preparadas si falla activación.
La recuperación deberá abstenerse hasta verificar una generación coherente vigente.

## Evidencias y límites

Evidencia duradera: [F4 inicial](../evidence/f4/initial-20261101/).
Incluye comandos/stdout/stderr, auditoría, manifiestos, copias SQLite de las ramas
y del puntero, reaperturas y cierre técnico. No sustituye evidencias anteriores.
Los datos operativos persisten en el volumen Docker bajo `artifacts/indexes/`.

F4 no certifica documentos, no calibra laya y no entrega búsqueda híbrida ni MCP.
Los eventos F2 permanecen pendientes; propagación/reconciliación corresponde a F10.
El próximo incremento técnico es F5 con `petroandes-recuperacion-mcp`.
Los esperados finales y decisiones positivas requieren revisión humana separada.
