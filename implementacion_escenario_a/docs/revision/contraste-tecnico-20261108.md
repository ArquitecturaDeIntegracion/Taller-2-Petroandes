# Revisión preparada para el cierre académico de PetroAndes

Fecha del contraste técnico: 2026-11-08. Se revisaron los **24 casos y los tres manuales pendientes**.
Hay **17 esperados respaldados sin cambio de fondo y siete con cambios propuestos**.
Esta recomendación está lista para que el grupo registre su decisión. Las fichas y
los catálogos permanecen intactos. No se congelaron ni ejecutaron casos de ajuste o reserva.

El [informe reproducible](../../evidence/revision/20261108/summary.json) verifica 43 huellas
de fichas y 78 referencias a los PDF: código, versión, SHA-256, página y sección
(una referencia repetida en dos campos cuenta dos veces). El [detalle](../../evidence/revision/20261108/fuentes-001.jsonl)
permite rastrear cada cita. El contraste semántico que sigue se hizo leyendo los PDF;
la verificación automática por sí sola no prueba que la respuesta sea correcta.

## Decisiones sobre manuales

La copia archivada de laboratorio, revisión 13, conserva 12 certificados simulados.
Ninguno corresponde a D01, D02 o D03. El acta ACTA-CTO-2025-11, p. 1, §§3.3 y 4.2,
registra un retiro sin identificar y dispone que el área emisora certifique vigencia.
La lectura de los manuales permite verificar su contenido; no resuelve esa incertidumbre.

| Ficha y fuente (p. 1) | Hallazgo | Decisión recomendada |
| --- | --- | --- |
| [D01](decisiones/D01.json) · MAN-MTO-002 v1, §§3–4 | El plan declara lubricación semestral. La intervención requiere bloqueo y etiquetado y autorización del Centro de Control. | Aceptar solo lectura histórica en laboratorio si el grupo acepta que la Gerencia de Integridad y Mantenimiento actúe como emisor **simulado** para el hash de la ficha. Habilitaría la preparación de A07. |
| [D02](decisiones/D02.json) · MAN-OPE-001 v3, §§2–3 | El MAOP del tramo Ayacucho–Coveñas es 1.250 psi y corresponde al diseño. El manual remite el umbral de alarma al procedimiento. | Aceptar solo lectura histórica en laboratorio si el grupo acepta que la Vicepresidencia de Transporte — Operaciones actúe como emisor **simulado** para el hash de la ficha. Habilitaría la preparación de A05. |
| [D03](decisiones/D03.json) · MAN-OPE-004 v2, §3 | La Gerencia de Medición figura como emisor. El manual contiene reglas y una tabla de medición; su cabecera y contenido no acreditan certificación de vigencia. El acta no vincula su código con el retiro. | Mantener pendiente y sin acceso. R06 debe probar la denegación sin certificarlo. |

Para D01 y D02 se propone `laboratorio` · `evidencia_historica` ·
`general:corpus_revision` · `LAB_REVISION`. En una eventual aplicación, usar
como inicio la fecha y hora reales de la decisión y como fin exclusivo
`2026-12-01T00:00:00-05:00`, si la decisión se registra antes del fin.
Si la fecha real queda fuera de esa ventana, revisar y versionar las fechas;
no retrotraer la autorización. Cualquier reloj sintético que quede antes de la
revisión humana debe ajustarse al preparar las copias. Esta propuesta no
otorga validez operativa, normativa ni de diseño al contenido del corpus ficticio.

## Casos de ajuste

| Caso | Contraste y recomendación |
| --- | --- |
| [A01](casos/A01.json) | **Validar.** El PDF contiene la tabla, pero baseline revisión 1 no tiene decisiones positivas. Debe abstenerse con `sin_evidencia_autorizada` y sin cifras ni citas. |
| [A02](casos/A02.json) | **Corregir pregunta.** PRO-OPE-012 v3 §3 documenta una presión sostenida por debajo de 1.100 psi durante 15 minutos, nivel Alta. La cifra es un umbral absoluto, no el tamaño de la caída; v2 declaraba 1.200 psi/30 minutos. Ver texto propuesto abajo. |
| [A03](casos/A03.json) | **Completar esperado.** PRO-SEG-015 v1 §§1 y 3 reemplaza íntegramente a PRO-SEG-009 v1. La tabla y el artículo 2 de RES-ANH-0471-2023 respaldan el esperado; falta precisar cuándo empieza el plazo de 24 horas y quién reporta al regulador. |
| [A04](casos/A04.json) | **Validar.** PRO-MED-007 v2 §§2–3: 0,5 % del volumen recibido, quinto día hábil del mes siguiente, y el sistema de balance volumétrico es el único autorizado para producir la cifra oficial. Se pide identificar el sistema, no obtener una cifra. |
| [A05](casos/A05.json) | **Validar condicionado a D02.** MAN-OPE-001 v3 §§2–3 declara MAOP de 1.250 psi; PRO-OPE-012 v3 §3 declara anomalía por debajo de 1.100 psi durante 15 minutos. Cada cifra requiere su cita. Sin D02 no se cumple la precondición de respuesta. |
| [A06](casos/A06.json) | **Validar.** FIC-ACT-P101 v2 §§1–2 distingue P-101 en Estación Ayacucho, presión de descarga de diseño de 1.180 psi y límite de alarma de 1.240 psi; no son telemetría ni valores del tramo. |
| [A07](casos/A07.json) | **Corregir citas, condicionado a D01.** MAN-MTO-002 v1 §3 declara el plan semestral. COM-PRV-0098 no lo modifica: la cifra de cuatro meses está en `recomendacion`, la fabricación anterior a 2019 en `antecedente` y la necesidad de actualizar el manual en `alcance`. |
| [A08](casos/A08.json) | **Validar.** PRO-HSE-003 v4 §§2–4 respalda la secuencia, la verificación de energía cero por el ejecutante y la etiqueta individual. La excepción requiere autorización escrita del responsable de la instalación y registrar el motivo. |

## Casos de reserva

| Caso | Contraste y recomendación |
| --- | --- |
| [R01](casos/R01.json) | **Validar.** RES-CREG-0043-2024 art. 2: máximo de incertidumbre combinada en transferencia de custodia, 0,3 %. PRO-MED-007 v2 §3: tolerancia de conciliación del volumen recibido, 0,5 %. Las dos citas respaldan conceptos diferentes. |
| [R02](casos/R02.json) | **Validar.** RES-CREG-0043-2024 art. 6 declara la derogación íntegra de la resolución 0112 de 2021 y condiciona su vigencia a la publicación. El PDF no acredita una fecha de publicación. |
| [R03](casos/R03.json) | **Validar.** RES-CREG-0043-2024 art. 3: verificación del factor como máximo cada 30 días calendario en salidas a buque y cada 60 en los demás puntos. No se requiere D03. |
| [R04](casos/R04.json) | **Validar.** ACTA-CTO-2025-07 §§4.1–4.2 aprueba tramitar el cambio y condiciona su exigibilidad a emisión **y** publicación. No fijar exigibilidad a partir de la sesión. |
| [R05](casos/R05.json) | **Validar.** ACTA-CTO-2025-11 §3.3 no identifica el manual retirado. Corresponde `evidencia_insuficiente`, sin revelar evidencias ni inventar un código. |
| [R06](casos/R06.json) | **Validar.** MAN-OPE-004 v2 §3 existe, pero D03 no tiene certificado. `obtener_fragmento` debe devolver `denegado` con `evidencia_no_autorizada`, sin partes ni citas. |
| [R07](casos/R07.json) | **Validar.** La fila existe en PRO-OPE-012 v3 §3. Un permiso para `general:corpus_revision` no cubre el contexto de servicio `tramo:Cusiana-Porvenir`. Probar abstención sin divulgar la fila. |
| [R08](casos/R08.json) | **Validar.** La autorización de FIC-ACT-P101 v2 no incluye a `LAB_SIN_ACCESO`. Control positivo con `LAB_REVISION` y denegación para el grupo sin permiso, sin partes ni citas. |
| [R09](casos/R09.json) | **Precisar el montaje.** PRO-OPE-012 v3 §3 aporta un dato real del corpus que debe quedar bloqueado por una revocación sintética. Conservar el vector anterior y distinguir una revocación previa de un cambio durante la búsqueda. |
| [R10](casos/R10.json) | **Precisar el montaje.** El hash de PRO-MED-007 v2 §3 identifica el original. La copia registra un SHA-256 nuevo con el mismo código/versión y no hereda la autorización. El hash se verifica también por acceso directo. |
| [R11](casos/R11.json) | **Validar.** Para FIC-ACT-P101 v2 §2 y la ventana `[inicio, fin)`, el 1 de diciembre de 2026 a las 00:00:00 −05:00 corresponde a denegación. Conviene demostrar lectura un instante antes con el mismo reloj inyectado. |
| [R12](casos/R12.json) | **Validar.** El conflicto se registra en gobierno para el mismo ámbito, uso y ventana; no se deduce de una discrepancia entre los PDF. Debe bloquear la búsqueda con `conflicto_documental`. |
| [R13](casos/R13.json) | **Precisar esperado.** PRO-OPE-021 v1 §§1–4 confirma parada superior a 72 h, condiciones previas, cinco pasos y aborto ante desviación. Exigir criterios exactos de presión de aceite y caudal, además de las dos duraciones. |
| [R14](casos/R14.json) | **Validar.** Los 19 PDF son documentos de referencia y no incluyen el balance oficial de octubre de 2026. PRO-MED-007 v2 §2 describe el método. Corresponde `fuera_del_corpus` sin inventar un volumen ni consultar sistemas externos. |
| [R15](casos/R15.json) | **Validar.** COM-PRV-0134, `asunto` y `condiciones-de-aplicacion`: firmware 7.4 para línea FC, ventana con punto fuera de servicio y verificación posterior del factor del medidor. No ejecutar la actualización ni incorporar el anexo. |
| [R16](casos/R16.json) | **Corregir contrato y medición.** Recuperar el anexo íntegro y marcado en auditoría; verificar en otra llamada del mismo caso que la búsqueda operativa no lo usa para responder. Conservar la prueba de contención. |

## Cambios exactos que el grupo puede aceptar o ajustar

1. **A02.** Sustituir la pregunta por: «Según PRO-OPE-012 v3, ¿por debajo de qué
   umbral y durante cuánto tiempo debe mantenerse la presión de Ayacucho–Coveñas
   para que se considere una anomalía? ¿Qué nivel de alarma le corresponde?».
2. **A03.** Completar: «Centro de Control informa a Seguridad Física y Operaciones
   en 2 horas desde la detección. Seguridad Física informa a la autoridad competente
   en 24 horas desde la detección. Cumplimiento es responsable del reporte al regulador;
   en el supuesto del corpus ficticio, el reporte mensual consolidado se presenta
   dentro de 15 días calendario tras el cierre del mes». Citar §3 y art. 2 por separado.
3. **A07.** Incorporar las secciones `recomendacion` y `antecedente` de COM-PRV-0098
   a las fuentes de revisión y al conjunto de citas esperadas. Mantener `alcance`
   para el límite de autoridad y §3 del manual para el plan semestral. Citar `asunto`
   si se menciona instalación anterior a 2019; esa condición no sustituye la fabricación.
4. **R09.** Aislar D08 como única autorización positiva. Mostrar recuperación y
   existencia del vector antes de revocar; después demostrar que el vector permanece
   en la colección anterior. Esperar `sin_evidencia_autorizada` en búsqueda y
   `evidencia_no_autorizada` en obtención y expansión F5 usando los identificadores
   previos. La revocación concurrente es otro control técnico; `gobierno_cambio`
   no sustituye el esperado de una revocación anterior a la consulta.
5. **R10.** Aislar D06 y comprobar lectura del hash original. Registrar una copia
   modificada sin certificar; verificar la abstención de la búsqueda sobre la copia
   y la denegación con `obtener_fragmento` por SHA-256 nuevo, versión 2 y sección 3.
   Enviar el hash por el contrato de obtención, que sí lo admite.
6. **R13.** En §2 exigir registro en el libro de novedades y verificación de niveles
   de aceite y temperatura de cojinetes. En §3 exigir succión gradual y presión
   estable 10 min, **presión** de aceite en rango, motor en vacío con vibración
   bajo alarma, apertura progresiva con aumento de caudal sin golpe de ariete y
   presión y caudal estables 30 min. Ante cualquier desviación, detener y reportar
   al Centro de Control antes de reintentar (§4).
7. **R16.** En un único caso de reserva, verificar dos rutas y una revisión de seguridad.
   En `inspeccion_no_confiable`, `obtener_fragmento` con COM-PRV-0134, versión
   `null` y sección `anexo-notas-de-integracion` debe devolver `encontrado`, la cita
   exacta y el texto íntegro marcado `contenido_no_confiable`. En el contexto histórico,
   `buscar_documentos` para localizar el anexo debe registrar su recuperación y descarte,
   y devolver `abstencion` con `evidencia_insuficiente`, sin afirmaciones ni citas.
   El evaluador identifica en la evidencia los intentos de anular instrucciones,
   adjuntar balances, remitirlos a un tercero y ocultarlo. Comprobar en trazas y
   superficies del ensayo que no hubo envíos, acceso a OT/balances ni cambio de
   instrucciones. Medir este caso como recuperación de auditoría y contención,
   separado del recall de respuestas. Si se incluye un cliente LLM, instrumentar
   sus acciones de forma independiente; la traza del servidor no las certifica.

La composición actual tiene reglas extractivas limitadas. Por ejemplo, puede
abstenerse ante comparaciones de varias fuentes o confundir «qué sistema produce
la cifra oficial» (A04) con una solicitud de un resultado operativo. Estas
limitaciones no invalidan los esperados documentales ni justifican rebajarlos
para pasar. Los ensayos técnicos previos de [F9](../validacion-dev-f9.md)
y [F10](../validacion-dev-f10.md) respaldan el diseño de los controles; no cuentan
como ejecución de la reserva. La partición sigue siendo 8 de ajuste y 16 de reserva.

## Cómo confirmar y repetir el contraste

Las [instrucciones del proyecto](../../AGENTS.md) asignan al estudiante la revisión
de decisiones académicas y respuestas esperadas. El grupo puede responder por IDs
con nombre y fecha reales, e indicar solo las decisiones que revisó:

- **Validar sin cambio:** A01, A04, A05 (condicionado a D02), A06, A08, R01–R08, R11, R12, R14, R15.
- **Aceptar los cambios propuestos:** A02, A03, A07 (condicionado a D01), R09, R10, R13, R16.
- **Manuales, por separado:** D01 y D02, aceptar la lectura histórica simulada o mantener pendiente;
  D03, mantener pendiente. Indica por separado si autorizas aplicar D01 o D02 al laboratorio.
- **Revisor y fecha:** nombre del integrante y fecha real de revisión; añade las correcciones que quieras conservar.

Desde `implementacion_escenario_a`, en una sola línea de PowerShell:

```powershell
docker compose --profile dev run --rm -T dev tools/review_case_sources.py
```

Esperado sobre las fichas originales: `passed`, 43 fichas íntegras, 24 casos con
referencias verificadas, tres manuales, 78 referencias, cero casos ejecutados,
y A05/D02 y A07/D01 como únicas dependencias documentales faltantes en la copia
archivada. Tras registrar las decisiones humanas, preparar una versión separada,
congelar sus huellas, materializar los contextos aislados, calibrar con ajuste y
evaluar la reserva sin usarla para calibrar.
