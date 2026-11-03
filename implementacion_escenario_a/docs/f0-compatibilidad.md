# F0: preparación y compatibilidad verificadas

Fecha: 2026-11-01 (America/Bogota). Responsable técnico: Codex.
Resultado: [15 comprobaciones aprobadas](../evidence/f0/closure-final.json).
Esto cierra F0, no la aplicación 3.2 ni sus controles finales.

## Tareas y evidencia

| Tarea | Resultado observado | Evidencia |
| --- | --- | --- |
| F0.1 | Instrucciones y fuentes consultadas, entregables conservados | [Extracto F0](../evidence/f0/plan-section/), cierre con hashes originales |
| F0.2 | 19 PDF legibles, 19 pares y huellas calculadas | [Auditoría](../evidence/f0/corpus.json) |
| F0.3 | Entorno aislado, CPU/RAM/Python/Node registrados | [Entorno final](../evidence/f0/environment-final.json) |
| F0.4 | 75 distribuciones fijadas; pip check sin conflictos | [Bloqueo](../requirements.lock), [evidencia](../evidence/f0/dependencies.json) |
| F0.5 | Qdrant inserta, prefiltra, persiste y rechaza otro dueño | [Almacenamiento](../evidence/f0/storage-fixed.json) |
| F0.6 | E5 384d y laya noul/choice reales en español | [E5](../evidence/f0/e5-materialized.json), [laya](../evidence/f0/laya-online.json) |
| F0.7 | Inspector real lista y llama herramienta mínima stdio | [Inspector](../evidence/f0/mcp-local/summary.json) y transcripciones adjuntas |
| F0.8 | Segunda carga sin red, tiempos/memoria/hashes observados | [E5 offline](../evidence/f0/e5-offline-timing.json), [laya offline](../evidence/f0/laya-offline.json) |

Qdrant no usó servidor ni snapshots. Conservó tres vectores y devolvió solo ID 1
con filtro de IDs y revisión 7, excluyendo un vecino más parecido y otro antiguo.
Tras cerrar, reabrió con el mismo resultado. Otro proceso recibió el error de
propietario único. SQLite probó persistencia y rollback; Pydantic rechazó tipo
inválido y BM25 conservó el token sintético p-101. Son sondas de compatibilidad;
no sustituyen las futuras pruebas del gobierno por todas las rutas.

## Modelos y observaciones

E5 conserva revisión, bundle y prefijos de 3.1. La diferencia máxima frente al
pooling promedio enmascarado y L2 manual fue 4,47e-8. El adaptador rechazó una
entrada de 2005 tokens antes de enviarla al modelo.

Laya usó el checkpoint multilingüe real fijado en el ADR. En la corrida offline:
`noul` positivo 0,9638 y negativo 0,008; `choice` eligió pertinente/no_pertinente.
Los cuatro resultados repiten la primera carga. Entradas, preguntas, etiquetas,
longitudes y probabilidades quedan en archivos por caso. El umbral 0,5 es
diagnóstico sintético; no se calibró para el corpus. Se rechaza un par excedido
antes de inferencia, sin truncamiento silencioso.

| Medida | E5, corrida offline de tiempos | laya, corrida offline |
| --- | --- | --- |
| Carga desde archivos | 1,392 s | 18,822 s |
| Primera inferencia tras carga | 0,301 s, lote consulta/pasaje | 0,412 s, noul positivo |
| Inferencia posterior | 0,0317 s, mismo lote repetido | 0,202–0,289 s, otros tres casos |
| Pico del proceso | 749.473.792 bytes | 2.433.650.688 bytes |

Son ensayos individuales en CPU con dos hilos, no percentiles ni un SLO.
La primera descarga/carga de laya registró 61,135 s de resolución/descarga y
15,374 s de carga. E5 tuvo un intento fallido antes de materializar archivos;
los 1,628 s posteriores reutilizan descargas y no son descarga en frío.
Los primeros informes E5 llamaban `warm_inference_seconds` a la primera inferencia
con modelo cargado. `e5-offline-timing.json` distingue primera inferencia y
repetición; es el usado en esta tabla.

## Fallos conservados y resueltos

- Python del PATH: shim pyenv sin versión. Se usa `.venv/Scripts/python.exe`.
- Red bloqueada por sandbox (WinError 10013): descargas con autorización.
- [SQLite inicial](../evidence/f0/storage.json): conexión abierta al limpiar el
  temporal; cierre explícito y repetición aprobada.
- [Inspector inicial](../evidence/f0/mcp/list/): catálogo/config incompatibles;
  configuración de sesión local de solo lectura y repetición aprobada.
- Inspector configura secretos en memoria: no necesita keychain ni persistencia global.
- [E5 online inicial](../evidence/f0/e5-online.json): enlace simbólico rechazado;
  archivos materializados con la misma revisión, sin cambiar permisos globales.
- Laya adaptó metadatos del tokenizador con su cargador oficial. Hashes antes y
  después y repetición concordante constan en el [ADR](adr-0005-entorno-f0.md).

No quedan incompatibilidades bloqueantes observadas en este camino de F0.
No se infiere una sesión efectiva de VS Code. Los logs completos se dividen en
partes de 160 líneas con `command.json`. `.venv` contiene dependencias y cachés
de terceros y está excluido del código fuente entregado y su validador.

## Repetir las sondas

Desde esta carpeta, elegir rutas de evidencia nuevas porque no se sobrescriben:

```powershell
& ./.venv/Scripts/python.exe -m pip install -r requirements.lock
& ./.venv/Scripts/python.exe -m pip check
& ./.venv/Scripts/python.exe -X utf8 tools/f0.py storage --output evidence/repeticion-storage.json
& ./.venv/Scripts/python.exe -X utf8 tools/f0.py e5 --offline --output evidence/repeticion-e5.json
& ./.venv/Scripts/python.exe -X utf8 tools/f0.py laya --offline --output evidence/repeticion-laya.json
& ./.venv/Scripts/python.exe -X utf8 tools/f0_mcp.py --output-dir evidence/repeticion-mcp
& ./.venv/Scripts/python.exe -m pytest -q tests
```

Para primera descarga, omitir `--offline`; modelos guardados en `.venv`.
El [bloqueo Inspector](../evidence/f0/inspector-lock.zip) contiene package.json y
pnpm-lock.yaml: extraer en `.venv/inspector` y ejecutar allí pnpm 11.25.0 con
`install --frozen-lockfile --ignore-scripts`. Node debe estar en PATH.
La instalación observada y el ejecutable pnpm exacto constan en
[command.json](../evidence/f0/inspector-install/command.json). No se instala globalmente.
La reproducción limpia completa corresponde a F11 y sigue pendiente.

Se avanzó F1 con matriz, contratos, doce esquemas y 25 pruebas. Ver
[contratos](contratos.md), [trazabilidad](trazabilidad.md) y
[propuesta académica](revision-academica.md). Se conservan cuatro exclusiones,
quince pendientes y cero certificaciones positivas creadas. Faltan catálogo,
ingesta, índices, recuperación, composición, herramientas finales y evaluación.
