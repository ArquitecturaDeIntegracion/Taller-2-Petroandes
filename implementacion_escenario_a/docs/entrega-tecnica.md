# Entrega técnica del Escenario A

Extrae el ZIP completo y abre la carpeta `implementacion_escenario_a`
desde la raíz extraída. El corpus y los documentos de diseño se encuentran
en esa misma raíz. El archivo `.sha256` que acompaña al ZIP permite
comprobar la descarga con PowerShell.

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath .\PetroAndes_Escenario_A_Entrega_Tecnica_F11_Revision_20261108.zip
```

El ZIP reúne el código, las fuentes, la configuración portable, las guías,
los catálogos de prueba, el inventario de licencias y las evidencias F11.
`MANIFIESTO/archivos-*.jsonl` contiene las huellas de los archivos
incluidos. En las copias de recibos antiguos que usan referencias de
ruta portables se indica también la huella original. Docker guarda los
modelos y artefactos en volúmenes fuera de la carpeta del código. Descarga
los modelos siguiendo la [guía de validación integral](validacion-dev-f11.md).

| Qué revisar | Dónde empezar |
| --- | --- |
| Estado y alcance de los resultados | [Resultados técnicos y pendientes académicos](f11-resultados.md). |
| Correspondencia con el diseño 3.1 | [Matriz de ADR y EIP](f11-diseno-eip.md) y [trazabilidad](trazabilidad.md). |
| Resultados observados y recibos | [Evidencia F11](../evidence/f11/20261108/README.md). |
| Demostración de las herramientas | [MCP Inspector](inspector-web.md) y [Copilot](copilot-vscode.md). |
| Revisión del grupo | [Decisiones humanas](revision/20261108-confirmada/autorizacion.md), [matriz congelada](revision/20261108-confirmada/matriz.md) y [evidencia de cierre](../evidence/revision/20261108-confirmada/README.md). |

Para comprobar rápidamente una copia extraída, ejecuta la preparación de
Docker y E5 de la [guía F11](validacion-dev-f11.md) y usa el mismo
`$proyecto` en PowerShell. La prueba reconstruye el baseline y hace una
consulta real con MCP Inspector.

```powershell
$salida = 'reports/portable/entrega-verificada-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
docker.exe compose -p $proyecto --profile dev run --rm -T -w /tmp dev /workspace/implementacion_escenario_a/tools/f11_verify_delivery.py --output-dir $salida
Get-Content -LiteralPath (Join-Path $salida 'summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
```

Espera `status: passed`, 92 fragmentos extraídos y 0 publicados en baseline,
la denegación de la versión excluida y una respuesta histórica para P-101.
El resultado histórico cita **1.180 psi** de diseño y **1.240 psi** de alarma.

Para la sustentación, usa el ejercicio de la [guía F11](validacion-dev-f11.md)
y escoge una pregunta nueva. Las decisiones del grupo ya están registradas.
La evaluación académica formal requiere publicar los índices de cada caso,
calibrar con ajuste y ejecutar la reserva.
