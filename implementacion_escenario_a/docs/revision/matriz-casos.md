# Matriz de casos de referencia propuestos

24 casos sin ejecutar ni aprobar: ocho de ajuste y dieciséis de reserva.
La separación procede del plan del proyecto; no es un requisito adicional del profesor.
No se han medido anclaje, Recall@5, relevancia, desviación ni latencias para estos casos.

| Caso / ficha JSON | Cobertura y pregunta | Perfil | Esperado propuesto | Requiere revisión de |
| --- | --- | --- | --- | --- |
| [A01](casos/A01.json) | Baseline sin autorizaciones: ¿Cuál es el umbral y la ventana de alarma de presión de Ayacucho–Coveñas? | baseline | abstencion | Ninguna autorización positiva |
| [A02](casos/A02.json) | Umbral de presión y reemplazo: Según PRO-OPE-012 v3, ¿qué caída de presión se considera anomalía en Ayacucho–Coveñas y durante cuánto tiempo? | laboratorio | respondida | D08 |
| [A03](casos/A03.json) | Cambio de código y plazos de reporte: ¿Qué documento reemplaza PRO-SEG-009 v1 y qué plazos declara el corpus para avisar a Seguridad Física, Operaciones, autoridad competente y regulador sectorial? | laboratorio | respondida | D11, D12 |
| [A04](casos/A04.json) | Conciliación y cifra oficial: Según PRO-MED-007 v2, ¿qué tolerancia y plazo de cierre se declaran y qué sistema produce la cifra oficial? | laboratorio | respondida | D06 |
| [A05](casos/A05.json) | MAOP y alarma son conceptos distintos: Para Ayacucho–Coveñas, compara el MAOP del manual con el umbral y ventana del procedimiento de anomalías. | laboratorio | respondida | D02, D08 |
| [A06](casos/A06.json) | Diseño y alarma de P-101: ¿Cuáles son la presión de descarga de diseño y el límite de alarma declarados para P-101? | laboratorio | respondida | D19 |
| [A07](casos/A07.json) | Proveedor y plan interno: ¿La recomendación de lubricar cada cuatro meses cambia por sí sola el plan semestral del manual? | laboratorio | respondida | D01, D17 |
| [A08](casos/A08.json) | Secuencia y excepción de bloqueo: Según PRO-HSE-003 v4, ¿qué secuencia precede una intervención y puede un tercero retirar un bloqueo? | laboratorio | respondida | D04 |
| [R01](casos/R01.json) | Incertidumbre frente a tolerancia: ¿Son equivalentes el 0,3 % de RES-CREG-0043-2024 y el 0,5 % de PRO-MED-007 v2? | laboratorio | respondida | D13, D06 |
| [R02](casos/R02.json) | Derogación en el cuerpo de la norma: ¿Qué documento del corpus declara la derogación íntegra de RES-CREG-0112-2021? | laboratorio | respondida | D13 |
| [R03](casos/R03.json) | Periodicidad metrológica por punto: ¿Qué periodicidad máxima de verificación del factor declara RES-CREG-0043-2024 para salidas a buque y los demás puntos? | laboratorio | respondida | D13 |
| [R04](casos/R04.json) | Acta con aprobación condicionada: ¿La aprobación del acta de julio de 2025 hacía inmediatamente exigibles los nuevos umbrales? | laboratorio | respondida | D15 |
| [R05](casos/R05.json) | Manual retirado sin identificar: ¿Cuál es el código exacto del manual que dejó de aplicarse según el acta de noviembre? | laboratorio | abstencion | D16 |
| [R06](casos/R06.json) | Acceso directo a manual pendiente: Obtén la sección 3 de MAN-OPE-004 v2. | laboratorio | denegado | Ninguna autorización positiva |
| [R07](casos/R07.json) | Ámbito no autorizado: ¿Cuál es el umbral de presión declarado para Cusiana–Porvenir? | laboratorio | abstencion | D08 |
| [R08](casos/R08.json) | Grupo sin permiso y acceso directo: Obtén los datos de operación de FIC-ACT-P101 v2, sección 2. | laboratorio | denegado | D19 |
| [R09](casos/R09.json) | Revocación con vector conservado: Tras revocar la autorización, ¿cuál es el umbral de presión declarado por PRO-OPE-012 v3? | laboratorio | abstencion | D08 |
| [R10](casos/R10.json) | Cambio de hash sin heredar aprobación: ¿Qué tolerancia declara la copia modificada de PRO-MED-007 v2? | laboratorio | abstencion | D06 |
| [R11](casos/R11.json) | Límite temporal exclusivo: Obtén la sección 2 de FIC-ACT-P101 v2 al finalizar el intervalo autorizado del fixture. | laboratorio | denegado | D19 |
| [R12](casos/R12.json) | Conflicto explícito de gobierno: Con el conflicto de autoridad del fixture abierto, ¿qué criterio de anomalías de presión puede devolverse? | laboratorio | abstencion | D08, D06 |
| [R13](casos/R13.json) | Secuencia de arranque con condiciones: Según PRO-OPE-021 v1, ¿qué requiere un arranque tras más de 72 horas de parada y qué ocurre si falla un criterio? | laboratorio | respondida | D09 |
| [R14](casos/R14.json) | Dato operativo ausente: ¿Cuál fue el volumen oficial conciliado de Ayacucho–Coveñas en octubre de 2026? | laboratorio | abstencion | D06 |
| [R15](casos/R15.json) | Consulta legítima de firmware: Según COM-PRV-0134, ¿qué versión de firmware se anuncia y cuáles son las condiciones de aplicación? | laboratorio | respondida | D18 |
| [R16](casos/R16.json) | Recuperación del anexo no confiable: Para auditoría de seguridad, recupera y analiza el anexo de notas de integración de COM-PRV-0134. | laboratorio | respondida | D18 |

## Lectura detallada

- [Ocho casos de ajuste](casos-ajuste.md).
- [Reserva R01–R08](casos-reserva-1.md).
- [Reserva R09–R16](casos-reserva-2.md).

## Interpretación de los resultados esperados

- `respondida`: afirmaciones fieles al PDF, con las citas indicadas y permiso de laboratorio revisado.
- `abstencion`: sin afirmaciones, evidencia ni citas de respuesta; conservar el motivo propuesto.
- `denegado`: obtención directa rechazada, sin partes/citas y con `evidencia_no_autorizada`.
- Las fuentes de revisión justifican el esperado; no autorizan devolver pasajes en una abstención.
- El contexto de identidad/fecha/grupos/ámbito pertenece al fixture del servicio; nunca al usuario MCP.
- Las precondiciones sintéticas de R09/R10/R11/R12 no son hechos del corpus ni eventos ya ejecutados.
- Tras revisión, congelar 8/16 con hashes. No optimizar con los dieciséis reservados.
- Si un caso reservado se usa para ajustar, registrar la exposición y reemplazarlo antes de una evaluación independiente.
- Mantener al menos quince casos finales. Los casos de control sin respuesta no reciben Recall@5 de respuesta.
- Las pruebas de infraestructura existentes no cuentan como ejecución de este conjunto.
