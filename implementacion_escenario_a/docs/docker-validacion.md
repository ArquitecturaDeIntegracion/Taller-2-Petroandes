# Docker comprobado y preparación para F2

Fecha: 2026-11-01, America/Bogota. Resultado: validación real aprobada.

Docker Desktop 4.43.2 expone el motor Linux 28.3.2, arquitectura x86-64.
La imagen `petroandes-educativo:local` se construyó y ejecutó correctamente.
El fallo anterior de `dockerInference` dejó de bloquear el proyecto al abrir Docker.

## Entorno observado

| Componente | Resultado |
| --- | --- |
| Python del contenedor | 3.12.16 |
| Node | 22.23.4 |
| PyTorch | 2.15.0+cpu; sin requisito de GPU |
| Inspector | 2.13.0, transporte stdio y SDK legacy |
| SQLite | 3.40.1 |
| Memoria disponible para Docker | Aproximadamente 8 GB totales |

Imagen de la batería completa:
`sha256:ac94ffcb9a82c3db401edeacb3d58bb7deca9545b6e7d75aeb834c4dfcf33acd`.
El inventario completo está en los logs `freeze-linux`; incluye hf-xet 1.8.0.
`environment.isolated = false` indica que no hay venv dentro de la imagen;
la ejecución usa el aislamiento del contenedor, separado del Python del host.

## Evidencia y resultados

La batería `tools/check_docker.py` aprobó **19 comprobaciones**:

- Motor, Compose, identidad de imagen, pip check e inventario de versiones.
- Inventario de fuentes y validador de estructura dentro de Linux.
- 36 pruebas en la imagen y 36 con el código local montado mediante `dev`.
- Qdrant: filtro previo, persistencia y rechazo de un segundo propietario.
- SQLite: persistencia y rollback; Pydantic y BM25 con controles sintéticos.
- 19 PDF legibles con hashes conservados.
- Inspector real: listado y llamada al servidor mínimo de F0.
- debugpy: breakpoint verificado y alcanzado, continuación y salida 0.
- Copia de modelos locales al volumen Docker sin sobrescribir, con hashes iguales.
- E5 offline: dimensión 384 y error de pooling manual 4,47 × 10^-8.
- Laya offline: cuatro casos sintéticos sin discrepancias; guarda de tokens activa.
- Cierre histórico F0 revalidado: 15 comprobaciones aprobadas.

Resultados locales bajo `reports/portable/docker-validacion-20261101/`:
`checks-final/summary.json`, informes de cada sonda y logs de comandos en partes
de máximo 160 líneas. `build-debug-corregido/` conserva la construcción comprobada.
Son informes generados y excluidos del repositorio; no se sobrescribió evidencia F0/F1.
Los intentos fallidos previos también permanecen disponibles para trazabilidad.

## Correcciones realizadas al verificar

1. Se precisó la excepción de `.env.example` en `Dockerfile.dockerignore` para
   evitar recorrer cachés locales excluidas con acceso restringido.
2. El registrador de comandos imprime UTF-8, incluso en una consola Windows CP1252.
3. La prueba DAP envía `disconnect` y cierra el socket al terminar. Esto evita
   que debugpy espere al cliente en Linux. También pasó la regresión en Windows.
4. El perfil `dev` monta el código local en lectura y conserva caché, artefactos
   e informes en montajes de escritura separados; comparte ese esquema con debug.

## Continuar F2 desde VS Code

Edita los archivos en el host y valida los cambios dentro de Docker:

```powershell
docker compose --profile dev run --rm dev tools/read_source.py plan --section "F2 Gobierno"
docker compose --profile dev run --rm dev -m pytest -q -p no:cacheprovider --basetemp artifacts/pytest-f2
docker compose --profile dev run --rm dev tools/validate_agent.py
```

`dev` refleja cambios de código sin reconstruir; si cambian dependencias o
Dockerfile, reconstruye con `docker compose build project`.
Los catálogos y datos generados de F2 deben ir bajo `artifacts/`, persistente en
el volumen Docker. No se ha implementado todavía el catálogo ni la elegibilidad.

Para repetir la batería desde el host con modelos locales ya disponibles:

```powershell
python tools/check_docker.py --output-dir reports/portable/docker-otra-corrida --seed-host-models
```

Usa un directorio nuevo. Si no copias modelos del host, carga antes E5/laya
en el volumen Docker con las sondas online del README; la batería usa offline.
La imagen probada contiene el código de esa construcción; `dev` usa el del host.

## Límites que permanecen

La prueba del adaptador no automatiza la interfaz de VS Code. MCP verifica el
servidor mínimo F0, no las dos herramientas finales de F7. Los casos sintéticos
no sustituyen los casos de referencia ni la revisión académica.
F1 sigue parcial. F2 puede iniciar catálogo y gobierno sin aprobar documentos:
se conservan **cuatro excluidos y quince pendientes**, sin autorizaciones nuevas.
No se completó F2 ni se acredita una instalación en otra máquina o macOS.
