# Validación de PetroAndes hasta F6 con Docker dev

Abre PowerShell en `implementacion_escenario_a` e inicia Docker Desktop con
contenedores Linux. El perfil `dev` monta el código local. Ejecuta por turnos
las consultas que apunten al mismo índice Qdrant.

## 1. Preparar y comprobar el entorno

```powershell
docker compose --profile dev build dev
docker compose --profile dev run --rm -T dev tools/validate_agent.py
docker compose --profile dev run --rm -T dev tools/preflight.py
```

**Esperado.** La construcción y el validador terminan con código 0. El preflight
lista 19 PDF, 19 Markdown de contraste, fuentes con `hash_matches: true` y
`errors: []`. El preflight es un inventario.
[Sondas de compatibilidad F0](f0-compatibilidad.md).

Si el volumen de modelos es nuevo, prepara E5 una vez con red y una ruta de
salida nueva. Se comprueban dos vectores finitos de 384 dimensiones.

```powershell
docker compose --profile dev run --rm -T dev tools/f0.py e5 --output reports/portable/validacion-f6-e5.json
```

## 2. Ejecutar la suite y los ejemplos citados

```powershell
docker compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider --basetemp /tmp/validacion-hasta-f6
docker compose --profile dev run --rm -T dev -m pytest -q -s -p no:cacheprovider --basetemp /tmp/validacion-f6 tests/test_f6_compose.py
```

**Esperado.** La suite completa pasa 178 pruebas y el bloque F6 pasa 22, ambos
con código 0. El bloque F6 imprime
las preguntas técnicas, las citas y las trazas con `correlation_id`. Puede
ejecutarse con los volúmenes de catálogos vacíos. Reingiere 19 PDF y verifica
la reapertura de 58 fragmentos correspondientes a 12 documentos con
certificación simulada, revisión 13. El reloj se fija solo en el ensayo
histórico, dentro del período ya registrado.

| Comprobación | Resultado esperado |
| --- | --- |
| Alarma de Caucasia–Coveñas | Cita PRO-OPE-012, versión 3, sección 3. Conserva la caída sostenida por debajo del umbral, la fila de 920 psi y la ventana de 15 minutos. |
| Descarga de P-101 | Cita la fila de FIC-ACT-P101, versión 2, sección 2, con 1.180 psi de diseño y 1.240 psi de alarma. |
| Incertidumbre y tolerancia | La resolución devuelve 0,3 % con su negación y `sin versión` en la cita. El procedimiento devuelve 0,5 % de tolerancia de conciliación. |
| Secuencia | Cita el alcance, las condiciones previas, todos los pasos y el criterio de aborto de PRO-OPE-021. Si falta una condición enlazada, el compositor rechaza la unidad. |
| Proveedor y acta | El extracto conserva el alcance de la recomendación, las condiciones de firmware y la condición de emisión y publicación del acta. |
| Peticiones ambiguas o insuficientes | `ambito_ambiguo` sin tramo, o con tramo del filtro distinto del mencionado. `evidencia_insuficiente` ante fuente equivocada, comparación o dirección de presión no respaldada. |
| Cifra oficial | `fuera_del_corpus` y listas de afirmaciones y evidencia vacías. |
| Anexo y cambio de gobierno | El anexo se identifica en la traza y la obtención autorizada lo conserva marcado. Al vencer los permisos durante la composición se devuelve `gobierno_cambio` con listas vacías. |

Estos ejemplos son pruebas técnicas separadas. Los casos académicos de ajuste
y reserva están pendientes de revisión. [Criterios del compositor](adr-0010-composicion-f6.md).

## 3. Probar la CLI con tu volumen habitual

Ejecuta este bloque si ya tienes los catálogos de las fases anteriores. Usa las
opciones por campo de la CLI en PowerShell.

```powershell
docker compose --profile dev run --rm -T dev tools/f5.py --profile baseline responder --consulta 'Umbral y ventana de anomalía de presión en Caucasia-Coveñas'
docker compose --profile dev run --rm -T dev tools/f5.py --profile laboratorio responder --consulta 'Presión de descarga y límite de alarma de P-101'
docker compose --profile dev run --rm -T dev tools/f5.py --profile laboratorio obtener --doc-id FIC-ACT-P101 --version 2 --seccion 2
```

| Comando | Resultado esperado con el contexto de despliegue |
| --- | --- |
| Responder en baseline | `abstencion`, `sin_evidencia_autorizada`, revisión 1 y listas vacías. |
| Responder en laboratorio | `abstencion`, `sin_evidencia_autorizada`, revisión 13 y listas vacías. |
| Obtener la ficha en laboratorio | `denegado`, `evidencia_no_autorizada`, partes y citas vacías. |

Los permisos simulados de revisión se registraron para otro contexto. Por eso
la prueba histórica puede mostrar extractos mientras que la CLI habitual se
abstiene. El JSON de `responder` incluye el contrato en `resultado`, una
representación legible en `texto` y diagnósticos en `traza`.

Para inspeccionar los catálogos, verificar la generación activa y probar
la recuperación de candidatos con `buscar`, sigue el paso 3 de la
[guía hasta F5](validacion-dev-hasta-f5.md#3-comprobar-el-estado-del-volumen-existente).
