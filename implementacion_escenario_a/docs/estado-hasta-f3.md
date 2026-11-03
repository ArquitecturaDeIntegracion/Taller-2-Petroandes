# Estado de reanudación

Actualizado: 2026-11-01, America/Bogota. Responsable técnico: Codex.

## Tarea activa

- F3 técnica verificada: **extracción y partición de los 19 PDF en Docker `dev`**.
- Revisión académica de F1/F2 pendiente; próximo incremento técnico independiente: F4.
- Los cambios F2/F3 se validaron en Linux con el código local montado en `dev`.
- F0 verificada: [cierre de 15 comprobaciones reales](../evidence/f0/closure-final.json).
- F1 iniciada: matriz R01–R10, modelos Pydantic y contratos MCP proyectados.
- Hay dos catálogos y generaciones F3 separadas; aún no hay índices activos ni servicio final.
- No hay aprobaciones académicas ni certificaciones positivas registradas.
- Baseline: cuatro excluidos, quince pendientes; ninguna vigencia inventada.

## Incrementos y evidencia

### Propuestas para revisión humana, 2026-11-01

Preparado [paquete de revisión](revision/README.md): matriz de 19 documentos y
24 casos propuestos (8 ajuste/16 reserva), con hashes, páginas, secciones F3,
supuestos explícitos y decisiones pendientes. Candidaturas limitadas de lectura
descriptiva en laboratorio; no autorizaciones operativas.
Las 19 fichas y 24 casos mantienen revisor, decisión y fecha sin registrar.
Casos no ejecutados ni congelados; no hay métricas nuevas ni importación al catálogo.
Baseline conserva cuatro excluidos y quince pendientes. La revisión técnica del
paquete no cierra F1/F2 ni sustituye la aceptación individual del estudiante.
El siguiente incremento técnico independiente continúa siendo F4.

### Portabilidad, 2026-11-01

Raíces centralizadas, lock portable, caché fuera de `.venv`, instalación editable,
perfiles debug y Docker/Compose preparados. Ver [resumen](resumen-portabilidad.md),
[ADR-0006](adr-0006-portabilidad.md) e [instrucciones](../README.md).
36 pruebas locales aprobadas; E5/laya offline, Inspector y breakpoint real debugpy
comprobados. Migración de 14 archivos de modelos con hashes conservados.
Cierre histórico F0: 15 comprobaciones aprobadas sin reescribir evidencia original.
Nuevos resultados locales en `reports/portable/` (ignorados al versionar).
Copia completa en otra ruta: inventario, validador y 36 pruebas aprobadas desde
un cwd externo; `relocation-final.json`. Reutilizó el intérprete instalado.
El primer intento Docker quedó bloqueado por `dockerInference`; ese bloqueo se
resolvió al abrir Docker Desktop y completar la validación descrita a continuación.
Este incremento no completa F1 ni cambia decisiones de gobierno del corpus.

### Docker y preparación F2, 2026-11-01

[Validación Docker](docker-validacion.md): imagen Linux construida, 19 comprobaciones
aprobadas, 36 pruebas en imagen y 36 en `dev`, SQLite/Qdrant, 19 PDF, Inspector,
breakpoint DAP y E5/laya offline. Laya: cuatro casos sin discrepancias.
Revalidación histórica F0: 15 comprobaciones aprobadas. Ninguna autorización nueva.
Se corrigieron exclusiones de contexto, salida UTF-8 y cierre DAP en Linux;
la regresión del breakpoint Windows también pasó.
Evidencia nueva: `reports/portable/docker-validacion-20261101/checks-final/`.
El perfil `dev` usa el código local con caché/artefactos persistentes; no necesita
reconstruir por cada edición. Reconstruir si cambian dependencias o Dockerfile.
Esa preparación no implementó F2 ni cerró los pendientes académicos de F1.

### F2 en Docker dev, 2026-11-01

Se ejecutaron validación, inventario y lectura F2 dentro de `dev`. Se implementaron
migración SQLite v1, historial por hash, observaciones PDF, relaciones, decisiones,
conflictos, revisión y eventos transaccionales. [Diseño y comandos](f2-gobierno.md).
Los perfiles baseline/laboratorio se inicializaron en archivos separados bajo
`artifacts/catalog/`: 19 documentos, cuatro excluidos, quince pendientes, cero
certificados y nueve relaciones por perfil; revisión 1 con un evento inicial.
No se cargaron decisiones humanas. El manual retirado no identificado sigue pendiente.

[69 pruebas aprobadas](../evidence/f2/initial-20261101/tests-readonly-final/) en dev,
incluyendo rechazo por hash/período/ámbito/uso/grupos, revocación, conflictos,
rollback técnico sin rehabilitar, idempotencia, fallos reales SQLite y CLI.
Otro proceso reabrió los catálogos y las copias: [resultado](../evidence/f2/initial-20261101/persisted-archive.json).
Confirmó cero elegibles, 19 accesos directos denegados por perfil y hashes PDF intactos.
La evidencia nueva se conservó en `evidence/f2/initial-20261101`, sin sustituir la previa.
[Validación final F2](../evidence/f2/initial-20261101/validate-final/): formatos,
enlaces y hashes correctos; máximo 194 líneas por archivo textual del proyecto.

### F3 en Docker dev, 2026-11-01

[F3 técnica verificada](f3-ingesta.md): 19 PDF preparados sin rechazos, 92 fragmentos
y 92 padres por perfil, 15 tablas y 62 filas. Tokenizador E5 real, revisión y hashes
fijados; máximo observado 291 tokens por input completo (límite 448).
Se conservaron secciones, artículos, condiciones, filas/cabeceras y el anexo no
confiable. Markdown solo contrastó la extracción; no construyó contenido.

[120 pruebas aprobadas](../evidence/f3/initial-20261101/tests-final/) y
[cierre técnico con copias SQLite](../evidence/f3/initial-20261101/closure-archived.json).
La reingesta final reutiliza generación y UUID sin duplicados. Las generaciones
son staging sin autorización, separadas por perfil. Gobierno F2 permanece en
revisión 1, cuatro excluidos, quince pendientes y cero certificados.
La [inspección visual](f3-revision-visual.md) cubrió las 19 páginas; los hashes de
los PDF del host y Docker coinciden. [ADR-0007](adr-0007-extraccion-estructural.md).
Evidencia final: `evidence/f3/initial-20261101`; corridas intermedias conservadas.
[Validación final F3](../evidence/f3/initial-20261101/validate-final/): sintaxis,
formatos, enlaces y hashes originales correctos; máximo 194 líneas por archivo textual.

| task_id | Estado | Archivos / comando / resultado |
| --- | --- | --- |
| F0.1–F0.2 | verificada | Validación, preflight, extracto F0 y [19 PDF legibles con hashes](../evidence/f0/corpus.json) |
| F0.3–F0.4 | verificada | `.venv`, [requirements.lock](../requirements.lock), [entorno](../evidence/f0/environment-final.json), pip check sin conflictos |
| F0.5 | verificada | `tools/f0.py storage`: Qdrant local, prefiltro, persistencia, único dueño, SQLite/Pydantic/BM25; [resultado](../evidence/f0/storage-fixed.json) |
| F0.6/F0.8 | verificada | E5 y laya con revisión, hashes, inferencia y segunda carga offline; [informe](f0-compatibilidad.md) |
| F0.7 | verificada | Inspector 2.13.0 real, stdio, listado y llamada mínima; [transcripciones](../evidence/f0/mcp-local/) |
| F1.1 | verificada | [Matriz inicial](trazabilidad.md), derivada de R01–R10 del plan |
| F1.2–F1.3 | en_curso | [Modelos y límites](contratos.md), doce esquemas; [25 pruebas aprobadas](../evidence/f1/contracts-tests-final/) |
| F1.4–F1.8 | pendiente | Casos del corpus y revisión humana; [propuesta](revision-academica.md) |
| F2.1/F2.3/F2.7 | verificada | Clasificación PDF, versiones nullable y nueve relaciones; [evidencia baseline](../evidence/f2/initial-20261101/baseline/) |
| F2.2/F2.4 | en_curso | Catálogos separados; revisión académica pendiente e índices reservados para F4 |
| F2.5/F2.6/F2.8 | verificada técnica | Política común y transacciones SQLite; [controles y alcance](f2-gobierno.md) |
| F3.1–F3.5 | verificada técnica | Inventario/hash, contraste, secciones y tablas; [manifiestos y trazas](f3-ingesta.md) |
| F3.6–F3.8 | verificada técnica | Input E5 <=448, UUID, padres, metadatos, contexto y anexo conservados |
| F3.9 | verificada técnica | Defecto inducido en copia: rechazo con motivo y cero fragmentos del documento |

Los `command.json` conservan ejecutable, argumentos, cwd, tiempos, código de salida
y archivos de stdout/stderr. Logs en partes de 160 líneas. Los informes individuales
no declaran toda F0 completa: la decisión agregada aparece en los informes de cierre.
El [informe F0](f0-compatibilidad.md) contiene comandos, medidas y límites.
[Validación histórica](../evidence/f0/validate-final-2/): formatos, enlaces y fuentes
correctos; máximo observado entonces: 185 líneas por archivo textual del proyecto.

## Fallos resueltos y decisiones

- Python del PATH es un shim pyenv sin versión; se usa Python 3.12.14 explícito
  de `.venv`. No se cambió configuración global.
- Red denegada por sandbox: descargas iniciales con autorización;
  las ejecuciones offline reales pasan sin red.
- SQLite necesitaba cierre explícito; Inspector rechazaba catálogo y config juntos.
  Se corrigieron las sondas y se conservaron resultados fallidos y exitosos.
- Caché E5 falló por enlaces simbólicos; archivos materializados resuelven el
  problema con la misma revisión. [ADR-0005](adr-0005-entorno-f0.md).
- Laya adapta metadatos del tokenizador con su cargador oficial; se conservan hashes
  anteriores/efectivos. Pesos y vocabulario no cambiaron; segunda carga concordante.
- Inspector usa almacén de secretos en memoria y configuración local de sesión.

## Bloqueos reales y límites

- F0: sin incompatibilidades bloqueantes observadas en el camino Windows probado.
- Docker: sin bloqueo observado en esta máquina; Linux y modelos CPU comprobados.
- F2: el sandbox denegó acceso al motor Docker; ejecución con autorización resolvió
  el acceso. No se modificó Docker global ni se reconstruyó la imagen.
- F3: fallos iniciales de celdas/cabeceras, considerando, encabezados nominales y
  comparación tupla/lista JSON corregidos; evidencia fallida conservada. Sin bloqueo técnico actual.
- Falta revisión del estudiante para decisiones positivas de laboratorio y esperados
  académicos. No bloquea crear catálogo, extracción o pruebas sintéticas.
- Cuatro casos laya y 25 pruebas de contratos no sustituyen los quince casos finales.
  Umbral noul 0,5 diagnóstico; calibración académica pendiente.
- Inspector verificó servidor mínimo F0, no las dos herramientas finales de F7.
- No se afirma compatibilidad de otra máquina, sesión efectiva VS Code ni SLO;
  reproducción limpia completa pendiente en F11. No hay repositorio Git en esta raíz.

## Próximo paso técnico

Leer F4 con `tools/read_source.py plan --section "F4 "` e implementar embeddings
e índices persistentes coherentes, reutilizando las generaciones finales F3.
Usar `docker compose --profile dev run --rm dev` seguido del comando Python
sin escribir `python`: el contenedor ya tiene ese entrypoint.
Usar `embeddings/input.py` y los input/huellas exactos de F3, sin truncar ni mezclar
bundles. Validar staging sin rechazos y revisión de gobierno antes de indexar/publicar.
Conservar elegibilidad externa a los vectores y único propietario de Qdrant local.
Completar las propuestas individuales y los casos F1 para revisión humana.
F1/F2 permanecen abiertas en su componente académico; el trabajo técnico puede
avanzar sin inventar autorizaciones. Recuperación/MCP y ataque se verificarán en F5/F7/F9.
