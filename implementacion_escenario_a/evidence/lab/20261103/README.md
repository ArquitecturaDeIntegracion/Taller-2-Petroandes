# Registro de certificaciones simuladas, 2026-11-03

Solo laboratorio. Revisor declarado por el usuario: Jonnathan Caballero.
Hora real de registro: `2026-11-03T00:12:31.781997-05:00`, America/Bogota.
Fin exclusivo: `2026-12-01T00:00:00-05:00`. Sin autoridad empresarial real.

| Evidencia | Contenido observado |
| --- | --- |
| `validate-start`, `preflight-start`, `docker-preflight` | Validación e inventario iniciales |
| `plan-f2`, `plan-f4`, `plan-f10` | Lecturas delimitadas del plan con hashes originales verificados |
| `prepare-request`, `administrative-inputs/` | Solicitud y doce fichas, con autorización conservada por hash |
| `tests-before-apply` | 45 pruebas aprobadas antes de mutar el catálogo |
| `state-before.json` | Huellas del catálogo/índices baseline, contexto y 24 casos |
| `register-run`, `registration/` | Doce decisiones, revisiones 2–13, eventos y copias SQLite antes/después |
| `register-repeat-run`, `registration-repeat/` | Repetición sin cambiar hora/revisión ni duplicar eventos |
| `state-after.json`, `state-final.json` | Estado real 12/3/4, permisos por uso, período y conservación de baseline/casos |
| `stale-index-denied` | Rechazo intencional del índice de revisión 1 ante gobierno 13; exit 1 esperado |
| `reconcile-run`, `reconciled.json` | Publicación de generación coherente 13 sin ampliar permisos |
| `check-index-run`, `index-closure/` | Reapertura, idempotencia y exportación de manifiestos/ramas/registro SQLite |
| `case-dependencies/` | A05/A07 con certificaciones faltantes; 24 revisiones humanas pendientes |
| `tests-full` | 145 pruebas aprobadas en Docker dev |
| `implementation-sha256.json` | Hashes calculados de entradas, código y documentación |
| `validate-final` | Comprobación final del paquete y originales |

Los comandos exactos, tiempos UTC, cwd y stdout/stderr constan en `command.json`.
Logs divididos en partes de 160 líneas; los datos JSONL conservan un registro por línea.

Los permisos solo cubren `general:corpus_revision` y `LAB_REVISION`. La configuración
existente del servicio tiene otro ámbito y grupo; continúa con cero elegibles.
Su índice se reconcilió a revisión 13 con ambas ramas vacías. El baseline y todos
sus archivos de índice conservan sus hashes. No se cambió el contexto para publicar
los doce documentos. Se verificó la política positiva por uso en el contexto aprobado.

Los trece eventos permanecen en outbox: no se simula un consumidor global F10.
No se modifican casos, esperados, manuales, exclusiones ni evidencias históricas.
No se ejecutó el anexo ni se accedió a OT ni se enviaron mensajes externos.
Los fixtures temporales de pruebas no son decisiones adicionales del catálogo real.

Ver [informe](../../../docs/certificacion-laboratorio-20261103.md),
[ADR](../../../docs/adr-0009-incorporacion-laboratorio.md) y
[estado](../../../docs/estado.md).
