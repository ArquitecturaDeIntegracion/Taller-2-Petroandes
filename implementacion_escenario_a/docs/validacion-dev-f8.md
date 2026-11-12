# Validación técnica de F8 en Docker dev

Ejecuta los comandos desde `implementacion_escenario_a` con Docker Desktop
en modo Linux y el volumen de modelos preparado. El arnés usa E5 y laya
multilingüe desde la caché. Si el volumen es nuevo, carga los modelos con las
sondas F0 de la [guía de Docker](docker-validacion.md).

```powershell
docker.exe compose --profile dev build dev
$salida = 'reports/portable/f8-tecnico-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker.exe compose --profile dev run --rm -T dev tools/f8_evaluate.py --output-dir $salida
```

Revisa el resumen después de que termine el comando.

```powershell
Get-Content -LiteralPath (Join-Path $salida 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
```

Los cuatro controles técnicos usan una copia del catálogo de laboratorio en la
revisión 13. Las llamadas Python y MCP se ejecutan por turnos para liberar el
índice local. Cada caso conserva el contexto, la entrada, el resultado, los
candidatos por rama, las citas, las latencias y las transcripciones del Inspector.

| Caso | Resultado esperado | Comprobación principal |
| --- | --- | --- |
| T01 | `abstencion` | Contexto habitual y motivo `sin_evidencia_autorizada`. |
| T02 | `denegado` | Contexto habitual y error `evidencia_no_autorizada`. |
| T03 | `respondida` | Ficha P-101 v2, sección 2, con diseño y alarma. |
| T04 | `respondida` | Resolución RES-CREG-0043-2024, artículo 2, con `0,3 %`. |

`status: passed` indica que los resultados observados coincidieron con los
controles técnicos, hubo paridad Python/MCP y se ejecutaron ambos juicios de
laya. El resumen conserva los juicios desfavorables, denominadores y fallos.
La suite técnica usa `top_k = 5` para medir Recall@5. La [guía de exposición](inspector-web.md)
usa `top_k = 3` en la interfaz web.

## Alcance de la evaluación

La procedencia se verifica contra los fragmentos elegibles del ensayo. Laya
evalúa por separado el respaldo de las afirmaciones con `noul` y la pertinencia
de los candidatos con `choice`. El evaluador revisa la longitud antes de
inferir y registra como no evaluables los pares que exceden el límite.
El umbral `0,5` es diagnóstico. `umbral_calibrado` queda en `null`.
[Implementación oficial de laya](https://github.com/NandhaKishorM/laya).

El arnés registra el estado de los casos propuestos sin ejecutarlos. La calibración y
la evaluación de reserva requieren [revisión humana](revision/README.md) y
materialización de sus contextos y respuestas esperadas. El campo
`evaluacion_formal_ejecutada` permanece en `false` durante la prueba técnica.
