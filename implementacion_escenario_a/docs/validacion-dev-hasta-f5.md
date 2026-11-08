# Validación de PetroAndes hasta F5 con Docker

Abre PowerShell en `implementacion_escenario_a`. Inicia Docker Desktop en modo
contenedores Linux y conserva la carpeta `corpus` en la raíz del taller.
Ejecuta los comandos en el orden indicado. El perfil Docker `dev` monta el código
local y los perfiles documentales `baseline` y `laboratorio` usan catálogos
separados. Qdrant local requiere que las consultas al mismo índice se hagan por turnos.

## 1. Construir y verificar el entorno

```powershell
docker compose --profile dev build dev
docker compose --profile dev run --rm -T dev tools/validate_agent.py
docker compose --profile dev run --rm -T dev tools/preflight.py
```

**Esperado.** La imagen se construye, el validador termina con `OK` y el preflight
informa 19 PDF, 19 representaciones Markdown, fuentes con `hash_matches: true`
y `errors: []`. El campo `phase_F0_complete: false` pertenece al inventario y
se complementa con los ensayos de la [fase F0](f0-compatibilidad.md).

Si el volumen de modelos es nuevo, prepara E5 una vez con red. Cambia el nombre
de salida si ya existe. El comando carga la revisión fijada y comprueba
dos vectores finitos de 384 dimensiones.

```powershell
docker compose --profile dev run --rm -T dev tools/f0.py e5 --output reports/portable/validacion-e5.json
```

## 2. Ejecutar los controles técnicos

```powershell
docker compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider --basetemp /tmp/validacion-petroandes
docker compose --profile dev run --rm -T dev -m pytest -q -s -p no:cacheprovider --basetemp /tmp/validacion-f5 tests/test_f5_retrieval.py tests/test_f5_selection.py tests/test_f5_corpus.py
```

**Esperado.** La suite completa pasa 156 pruebas y el bloque F5 pasa 11, ambos
con código 0. El bloque F5 imprime trazas por rama, IDs seleccionados, tiempos
y `correlation_id`. Puedes repetirlo con el volumen de catálogos vacío, porque
reconstruye sus índices en temporales del contenedor.

| Comprobación | Resultado esperado |
| --- | --- |
| PDF y publicación aislada | Se preparan 19 PDF y 92 fragmentos. Se publican y reabren 58 fragmentos de 12 documentos con certificación histórica simulada, revisión 13. |
| Códigos | `PRO-SEG-015 v1`, `RES-CREG-0043-2024` y `P-101` recuperan sus documentos. `P101` es un alias explícito del equipo. |
| Pregunta reformulada | La consulta de duración y presión para Ayacucho–Coveñas recupera candidatos de `PRO-OPE-012`. |
| Prefiltro real | El competidor sintético sigue primero en la consulta de control sin filtro. En F5 se ve el filtro Qdrant por ID, generación, revisión y bundle. El competidor no aparece en densa, BM25 ni códigos exactos. |
| Cambio de gobierno | La revocación conserva los datos físicos, la búsqueda en curso se abstiene con `gobierno_cambio` y la anterior generación queda bloqueada para consultas nuevas. |
| Obtención y expansión | El acceso positivo devuelve partes ordenadas y citas. La fuente revocada o vencida da `denegado`. El selector exige hash ante varias emisiones elegibles con el mismo código y versión. |
| Código anterior | La búsqueda aislada `PRO-SEG-009 v1` se abstiene y el acceso directo se deniega. |

La prueba de corpus usa la copia de la revisión 13 y fija el reloj en el instante
registrado de la decisión, solo dentro del test. Utiliza el grupo `LAB_REVISION`,
el ámbito `general:corpus_revision` y el uso `evidencia_historica` de los permisos
registrados. Los casos académicos de ajuste y reserva requieren revisión humana.

## 3. Comprobar el estado del volumen existente

Ejecuta este bloque si Docker ya tiene los catálogos de las fases anteriores.
Si el catálogo no existe, puedes completar los pasos 1 y 2 con el repositorio y
la caché E5. Para inicializar un catálogo vacío, consulta la
[guía F2](f2-gobierno.md). El estado del laboratorio de la tabla corresponde al
volumen que recibió las [decisiones del 3 de noviembre](certificacion-laboratorio-20261103.md).

En PowerShell usa las opciones de la CLI. Algunos modos de PowerShell eliminan
las comillas internas al pasar JSON como argumento a Docker. Para obtener una
emisión sin versión, usa `--sin-version` en lugar de `--version`.

```powershell
docker compose --profile dev run --rm -T dev -m petroandes.catalog status --profile baseline
docker compose --profile dev run --rm -T dev -m petroandes.catalog status --profile laboratorio
docker compose --profile dev run --rm -T dev tools/f5.py --profile baseline buscar --consulta PRO-SEG-015 --top-k 3
docker compose --profile dev run --rm -T dev tools/f5.py --profile laboratorio buscar --consulta P-101 --top-k 3
docker compose --profile dev run --rm -T dev tools/f5.py --profile laboratorio obtener --doc-id FIC-ACT-P101 --version 2 --seccion 2
```

| Comando | Resultado esperado en el volumen validado |
| --- | --- |
| Estado baseline | Revisión 1, 19 documentos, 4 excluidos, 15 pendientes y 0 certificados. |
| Estado laboratorio | Revisión 13, 19 documentos, 4 excluidos, 3 pendientes y 12 certificados simulados. |
| Ambas búsquedas | `estado: abstencion`, `motivo_abstencion: sin_evidencia_autorizada` y trazas sin etapas de embedding ni ranking. |
| Obtener la ficha en laboratorio | `estado: denegado`, `error: evidencia_no_autorizada`, `partes: []` y `citas: []`. |

El servicio lee su grupo y ámbito de [la configuración de despliegue](../config/f4-context.json).
Ese contexto explica la diferencia entre las consultas del volumen y el ensayo
histórico aislado. Los UUID y los tiempos de la traza cambian en cada ejecución.

Para comprobar la generación activa de laboratorio y su consistencia F4,
escribe el resultado en un archivo nuevo.

```powershell
docker compose --profile dev run --rm -T dev tools/f4.py inspect --profile laboratorio --output reports/portable/validacion-f4-lab.json
```

**Esperado.** Manifiesto de revisión 13, `fragmentos: []` y bundle E5 de 384 dimensiones.
La salida F5 `recuperada` contiene pasajes y citas para F6. Las respuestas
extractivas se implementarán en F6 y la interfaz MCP se verificará en F7.
