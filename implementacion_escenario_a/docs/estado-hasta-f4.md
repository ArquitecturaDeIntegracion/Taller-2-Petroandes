# Estado de reanudación

Actualizado: 2026-11-01, America/Bogota. Responsable técnico: Codex.

## Tarea activa

- **F4 técnica implementada y verificada en Docker `dev`**: E5 y publicación
  coherente de fragmentos, Qdrant y rama léxica, con manifiestos persistentes.
- Próximo incremento técnico independiente: **F5, recuperación híbrida gobernada**.
- F1/F2 siguen abiertas en su componente académico. No hay decisiones positivas
  ni certificaciones nuevas. Las propuestas humanas siguen sin importar al catálogo.
- Baseline y laboratorio: 19 documentos, cuatro excluidos, quince pendientes,
  cero certificados y revisión 1. Cada perfil tiene una generación activa vacía.
- El servicio final y las dos herramientas MCP aún no están implementados.

## Evidencia F4, 2026-11-01

[Implementación, comandos y medidas](f4-indices.md),
[decisión de publicación](adr-0008-publicacion-f4.md) y
[evidencia duradera](../evidence/f4/initial-20261101/).

Se ejecutaron primero validador, preflight y lectura F4 mediante `read_source.py`.
El adaptador E5 verifica nueve archivos contra hashes F0, revisión de tokenizador,
prefijos, pooling, normalización y versiones efectivas. Rechaza inputs excedidos
y bundles distintos aunque tengan 384 dimensiones.

Auditoría separada de 92 fragmentos: 92 × 384 vectores finitos, normas entre
0,9999999404 y 1,0000001192. CPU, lotes de cuatro, 23 lotes; 8,727 s acumulados
de inferencia y 8,898 s de generación/guardado. RSS máximo de las muestras al
terminar lotes: 1229,633 MiB; no es un pico continuo ni un SLO.
Delta máximo de pooling manual: 6,5193 × 10⁻⁸. Los vectores de auditoría no son
una colección consultable y no autorizan documentos pendientes.

Publicación filtra por gobierno antes de crear las dos ramas. Verifica ambas,
IDs, hashes, payloads y revisión; activa un puntero SQLite bajo barrera de gobierno.
La apertura falla ante revisión/contexto/bundle distintos, corrupción o permisos
vencidos. El catálogo publicado conserva el gobierno de ingesta como procedencia,
separado de la revisión vigente y del registro externo que concede permisos.

| Perfil | Generación activa | Fragmentos / puntos |
| --- | --- | --- |
| baseline | `1589c208-0450-5b25-b58c-d61373aa340d` | 0 / 0 |
| laboratorio | `15ca08a0-c114-548d-8aaf-249e24211178` | 0 / 0 |

[134 pruebas aprobadas](../evidence/f4/initial-20261101/tests-final/) en `dev`:
E5/Qdrant reales, publicación sintética no vacía, reapertura en otro proceso,
idempotencia, dueño único, filtros, hash cambiado, revocación, vencimiento,
carreras y rollback por fallo SQLite. Alterar vectores, payloads, manifiesto o
cualquier rama bloquea la apertura. Las decisiones ficticias viven en temporales
de pruebas; no se modificaron decisiones ni propuestas del corpus real.

Las reejecuciones de los perfiles reales conservan generación y colección sin
duplicados. Se exportaron manifiestos, recibos y copias SQLite de cada rama y
del registro de publicaciones; Qdrant se reconstruye desde las fuentes, sin usar
snapshots nativos. Los datos operativos permanecen en el volumen Docker.
No se consumieron todavía los eventos pendientes F2; reconciliación en F10.
[Cierre técnico exportado](../evidence/f4/initial-20261101/closure/closure.json) y
[validación final del paquete](../evidence/f4/initial-20261101/validate-final/).

## Continuidad anterior

El [estado hasta F3](estado-hasta-f3.md) conserva íntegro el historial anterior,
incluidos bloqueos resueltos y enlaces. No se reescribieron los entregables del taller.

| Fase | Estado técnico y evidencia |
| --- | --- |
| F0 | Verificada: [15 comprobaciones reales](../evidence/f0/closure-final.json) |
| F1 | Parcial: [contratos](contratos.md), [propuestas humanas](revision/README.md) sin aprobar |
| F2 | Verificada técnicamente: [gobierno y catálogo](f2-gobierno.md), 69 pruebas históricas |
| F3 | Verificada técnicamente: [19 PDF, 92 fragmentos/padres](f3-ingesta.md), 120 pruebas históricas |
| F4.1–F4.4 | Verificadas: bundle E5 real, vectores, payload, CPU y consumo observado |
| F4.5–F4.7 | Verificadas técnicamente: subconjunto autorizado, activación íntegra, propietario único |

Los recibos `command.json` conservan ejecutable, argumentos, cwd, tiempos,
salida y código observado. Logs divididos en partes de 160 líneas.
Docker `dev` monta código local; no requiere reconstrucción por estas ediciones.
No cambiaron dependencias, configuración global ni originales registrados.

## Bloqueos reales y límites

- Sin bloqueo técnico actual observado para F4 en esta máquina y este contenedor.
- Docker requiere acceso al motor fuera del sandbox; se ejecutó con autorización.
- Faltan revisión humana de decisiones positivas de laboratorio y esperados finales.
  Por eso los índices reales están vacíos; no bloquea pruebas técnicas sintéticas.
- Cuatro casos laya de F0 no sustituyen la evaluación final ni su calibración.
- Inspector solo verificó el servidor mínimo F0; herramientas finales pendientes F7.
- No se afirma reproducción limpia F11, compatibilidad de otra máquina ni SLO.
- Python del PATH sigue siendo shim pyenv; usar `.venv/Scripts/python.exe` en host
  o el entrypoint Python del contenedor. No hay repositorio Git en esta raíz.

## Próximo paso técnico

Usar `petroandes-recuperacion-mcp`, leer F5 con `tools/read_source.py` y desarrollar
búsqueda densa + BM25 y códigos exactos con elegibilidad previa en ambas ramas,
RRF, relaciones y revalidación antes de devolver. El contexto del servicio es
interno: no aceptar perfil, grupos o fecha concedidos por una llamada MCP.
Reutilizar `index/`, `EligibilityService`, los manifiestos y los inputs F3 exactos.
Mantener un único propietario Qdrant; ejecutar CLI/evaluador por turnos.
La composición extractiva y abstenciones corresponden a F6; Inspector real a F7.
Continuar sin importar decisiones ni esperados académicos no revisados.
