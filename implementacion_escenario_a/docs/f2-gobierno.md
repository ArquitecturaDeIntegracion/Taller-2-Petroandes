# F2: catálogo y gobierno inicial en Docker dev

Fecha: 2026-11-01, America/Bogota. Responsable técnico: Codex.
Estado: base técnica verificada; revisión académica pendiente. F2 no se declara cerrada.
Se usó `docker compose --profile dev run --rm dev`, con el código local montado;
no se reconstruyó la imagen ni se cambió configuración global.

## Resultado observado

Dos catálogos SQLite separados, cada uno con 19 documentos lógicos, cuatro
excluidos, quince pendientes, cero certificados y nueve relaciones documentales.
La carga inicial completa crea revisión de gobierno 1 y un evento pendiente,
en una sola transacción. Se conservaron copias SQLite verificadas por SHA-256.
Ambos catálogos deniegan elegibilidad a los 19 documentos mientras no haya decisión.

- [Baseline: resumen y copia](../evidence/f2/initial-20261101/baseline/).
- [Laboratorio: resumen y copia](../evidence/f2/initial-20261101/laboratorio/).
- [Reapertura, hashes y acceso denegado](../evidence/f2/initial-20261101/persisted-archive.json).
- [69 pruebas aprobadas en dev](../evidence/f2/initial-20261101/tests-readonly-final/):
  36 anteriores y 33 de F2. Son controles técnicos; no casos académicos de referencia.
- [Sección F2 leída con read_source](../evidence/f2/initial-20261101/plan/).
- [Validación final](../evidence/f2/initial-20261101/validate-final/): máximo 194 líneas.

La evidencia duradera está en `evidence/f2/initial-20261101`. La ejecución produjo
primero informes nuevos en `reports/portable/f2-20261101`; se copiaron sin sustituir
evidencias anteriores. Cada ejecución conserva comando, resultado, tiempos y logs.

## Interfaces y responsabilidades

| Módulo | Responsabilidad |
| --- | --- |
| petroandes/catalog/schema.py | Migración inicial v1, metadatos, historial, relaciones, decisiones, conflictos y outbox |
| petroandes/catalog/api.py | Interfaz interna de lectura y mutaciones transaccionales |
| petroandes/catalog/store.py | Apertura explícita, perfiles y revisión esperada; abrir no crea archivos ausentes |
| petroandes/catalog/documents.py | Registro de documentos y huellas sin heredar autorización al cambiar contenido |
| petroandes/catalog/decisions.py | Historial inmutable de decisiones y resolución explícita de conflictos |
| petroandes/catalog/snapshot.py | Lectura consistente y rechazo de inconsistencias del catálogo |
| petroandes/governance/baseline.py | Cuatro exclusiones contrastadas en PDF; ninguna certificación positiva |
| petroandes/governance/pdf_metadata.py | Encabezados preliminares PDF, identidad, versión nullable, emisor y huella |
| petroandes/governance/eligibility.py | Política común para candidatos, referencia directa y futura expansión |

Se reutilizan los modelos Pydantic de F1. Las observaciones de evidencia y las
decisiones humanas son tablas y modelos distintos. La CLI administrativa permite
inicializar y consultar estado; no importa ni inventa aprobaciones.
Una decisión académica exige responsable, rol, supuesto, evidencia, hash, uso,
ámbito y período. Un nombre escrito en un campo no demuestra revisión humana;
la incorporación de decisiones reales del grupo queda pendiente de esa revisión.

Los datos residen en `artifacts/catalog/baseline/catalog.sqlite3` y
`artifacts/catalog/laboratorio/catalog.sqlite3`, dentro del volumen Docker.
`petroandes/paths.py` gobierna esas raíces con `PETROANDES_ARTIFACTS_DIR` opcional.
Se reservan `artifacts/indexes/baseline` y `artifacts/indexes/laboratorio`; todavía
no se construyen índices. Las referencias PDF son POSIX relativas con base `project:`.

## Controles comprobados

- Elegibilidad exige decisión vigente para el hash actual, autenticidad verificada,
  ámbito y uso exactos, intersección de grupos y ausencia de conflicto abierto.
- Recomendación no habilita instrucción operativa. El contenido sigue siendo dato
  no confiable aunque exista una decisión; no puede conceder privilegios.
- Pendientes, excluidos, vencidos, revisión futura, hash o ámbito incorrecto y grupos
  ajenos no entran al conjunto candidato. La referencia directa usa la misma política.
- El período es `[inicio, fin)`; fin null requiere intervalo abierto expresamente
  aprobado. El reloj operativo pertenece al servicio; la fecha se inyecta solo en pruebas.
- Un conflicto activo bloquea el ámbito/uso, sin elegir la fuente más similar.
  Detectar semánticamente incompatibilidades sigue siendo responsabilidad de revisión.
- Cambiar el PDF deja la autorización anterior inutilizable. Volver técnicamente al
  hash antiguo no restaura el permiso: también se exige una decisión posterior al registro.
- Una revocación conserva texto e historial. Los ensayos F2 no prueban todavía un
  vector revocado persistente: esa integración corresponde a F5/F10.
- Revisiones obsoletas de escritura se rechazan. Un fallo real inducido al insertar
  el evento deshace decisión y revisión juntas. Las repeticiones idénticas son idempotentes.
- Catálogo ausente, perfil equivocado, migración desconocida, referencias/payload
  corruptos o revisión incoherente causan indisponibilidad; no amplían la consulta.

Se preservan relaciones con predecesores ausentes sin crear documentos ficticios.
Una versión declarada «—» sigue siendo null. El manual retirado no identificado
permanece incierto. COM-PRV-0134 se conserva; no se ejecutó contenido del anexo.

## Comandos disponibles

Desde la raíz de implementación, con el motor Linux iniciado:

```powershell
docker compose --profile dev run --rm dev -m petroandes.catalog status --profile baseline
docker compose --profile dev run --rm dev -m petroandes.catalog status --profile laboratorio
docker compose --profile dev run --rm dev -m pytest -q -p no:cacheprovider --basetemp artifacts/pytest-f2-repeticion
docker compose --profile dev run --rm dev tools/check_f2.py --evidence-dir evidence/f2/initial-20261101 --output reports/portable/f2-repeticion.json
```

La inicialización ya ejecutada fue `-m petroandes.catalog init --profile baseline
--evidence-dir reports/portable/f2-20261101/baseline` y su equivalente laboratorio.
`init` rechaza sobrescrituras; no borres los volúmenes para repetir una prueba.
Usa directorios nuevos de evidencia y pruebas. El contenedor ya tiene entrypoint Python.

## Pendiente

Revisión humana de autorizaciones académicas y esperados de F1. F2 conserva ese
pendiente y no registra certificaciones ficticias. Los catálogos separados están
probados; los índices separados se construirán en F4. Recuperación e integración
de la política con herramientas MCP finales corresponden a F5/F7.
El próximo incremento independiente es F3: extracción y partición estructural PDF,
con trazabilidad y revisión de tablas, sin habilitar consulta operativa por defecto.
