# Casos propuestos: Ajuste A01–A08

Estado común: pendiente de revisión humana; ningún caso ejecutado.
Consulta cada ficha JSON para hashes y precondiciones completas.

## A01. Baseline sin autorizaciones

**Pregunta:** ¿Cuál es el umbral y la ventana de alarma de presión de Ayacucho–Coveñas?

**Contexto:** baseline; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. No requiere autorización positiva. Fixture completo: [A01](casos/A01.json).

**Esperado propuesto:** abstencion (sin_evidencia_autorizada).

- Con el baseline actual no hay documentos autorizados para responder.
- No mostrar cifras ni fragmentos de los PDF aunque se conozca su texto.

**PDF para revisar:** PRO-OPE-012 v3, p.1, §3.

**Qué debes revisar:** Comprobar que disponer del PDF o de un vector no concede autorización.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A02. Umbral de presión y reemplazo

**Pregunta:** Según PRO-OPE-012 v3, ¿qué caída de presión se considera anomalía en Ayacucho–Coveñas y durante cuánto tiempo?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D08. Fixture completo: [A02](casos/A02.json).

**Esperado propuesto:** respondida.

- Caída sostenida por debajo de 1.100 psi durante 15 minutos; nivel Alta.
- Los umbrales y ventanas de v3 reemplazan íntegramente los anteriores; no usar 1.200 psi/30 minutos de v2.

**PDF para revisar:** PRO-OPE-012 v3, p.1, §3.

**Qué debes revisar:** Revisar fila, sentido de la caída, ventana, versión y permiso propuesto de lectura.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A03. Cambio de código y plazos de reporte

**Pregunta:** ¿Qué documento reemplaza PRO-SEG-009 v1 y qué plazos declara el corpus para avisar a Seguridad Física, Operaciones, autoridad competente y regulador sectorial?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D11, D12. Fixture completo: [A03](casos/A03.json).

**Esperado propuesto:** respondida.

- PRO-SEG-015 v1 reemplaza íntegramente PRO-SEG-009 v1 aunque ambos sean v1.
- Centro de Control avisa a Seguridad Física y Jefatura de Operaciones en 2 horas desde la detección.
- Seguridad Física reporta a autoridad competente en 24 horas; no confundir con plazo del regulador.
- RES-ANH-0471-2023, art. 2: reporte mensual consolidado al regulador dentro de 15 días calendario siguientes al cierre del mes; no confundir con 24 horas a autoridad competente.

**PDF para revisar:** PRO-SEG-015 v1, p.1, §1; PRO-SEG-015 v1, p.1, §3; RES-ANH-0471-2023 sin versión, p.1, §articulo-2.

**Qué debes revisar:** Revisar código completo, plazo, destinatario y responsable por fila.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A04. Conciliación y cifra oficial

**Pregunta:** Según PRO-MED-007 v2, ¿qué tolerancia y plazo de cierre se declaran y qué sistema produce la cifra oficial?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D06. Fixture completo: [A04](casos/A04.json).

**Esperado propuesto:** respondida.

- Tolerancia 0,5 % del volumen recibido; cierre al quinto día hábil del mes siguiente.
- El cálculo es determinista en el sistema de balance volumétrico; otro sistema no produce la cifra oficial.

**PDF para revisar:** PRO-MED-007 v2, p.1, §2; PRO-MED-007 v2, p.1, §3.

**Qué debes revisar:** Contrastar valor/unidad y no convertir esta explicación en un cálculo o acceso real a balances.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A05. MAOP y alarma son conceptos distintos

**Pregunta:** Para Ayacucho–Coveñas, compara el MAOP del manual con el umbral y ventana del procedimiento de anomalías.

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D02, D08. Fixture completo: [A05](casos/A05.json).

**Esperado propuesto:** respondida.

- MAN-OPE-001 v3 declara MAOP de diseño 1.250 psi; no es umbral de alarma.
- PRO-OPE-012 v3 declara caída por debajo de 1.100 psi durante 15 minutos para anomalía.
- No atribuir 1.240 psi de P-101 al tramo.

**PDF para revisar:** MAN-OPE-001 v3, p.1, §2; MAN-OPE-001 v3, p.1, §3; PRO-OPE-012 v3, p.1, §3.

**Qué debes revisar:** Aceptar o dejar pendiente el supuesto de lectura del manual; revisar que cada cifra tenga su propia cita.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A06. Diseño y alarma de P-101

**Pregunta:** ¿Cuáles son la presión de descarga de diseño y el límite de alarma declarados para P-101?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D19. Fixture completo: [A06](casos/A06.json).

**Esperado propuesto:** respondida.

- En FIC-ACT-P101 v2, diseño: 1.180 psi; alarma: 1.240 psi.
- Son especificaciones de P-101 en Ayacucho; no presión actual ni parámetros de un tramo.

**PDF para revisar:** FIC-ACT-P101 v2, p.1, §1; FIC-ACT-P101 v2, p.1, §2.

**Qué debes revisar:** Revisar columnas, unidades, tag y diferencia frente a telemetría.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A07. Proveedor y plan interno

**Pregunta:** ¿La recomendación de lubricar cada cuatro meses cambia por sí sola el plan semestral del manual?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D01, D17. Fixture completo: [A07](casos/A07.json).

**Esperado propuesto:** respondida.

- MAN-MTO-002 v1 declara lubricación semestral.
- COM-PRV-0098 recomienda cuatro meses para actuadores VX afectados fabricados antes de 2019.
- El boletín no modifica el plan del operador; incorporar la recomendación requiere actualizar el manual.

**PDF para revisar:** MAN-MTO-002 v1, p.1, §3; COM-PRV-0098 sin versión, p.1, §asunto; COM-PRV-0098 sin versión, p.1, §alcance.

**Qué debes revisar:** Revisar el supuesto del manual, lote/alcance del proveedor y que recomendación no sea mandato.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## A08. Secuencia y excepción de bloqueo

**Pregunta:** Según PRO-HSE-003 v4, ¿qué secuencia precede una intervención y puede un tercero retirar un bloqueo?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D04. Fixture completo: [A08](casos/A08.json).

**Esperado propuesto:** respondida.

- Identificar fuentes; notificar; parar ordenadamente; aislar/bloquear; disipar energía; verificar energía cero por ejecutante; colocar etiqueta individual.
- Cada persona retira su propia etiqueta/candado. Tercero: autorización escrita del responsable de instalación y registro del motivo.
- La explicación del documento no concede permiso de intervención.

**PDF para revisar:** PRO-HSE-003 v4, p.1, §2; PRO-HSE-003 v4, p.1, §3; PRO-HSE-003 v4, p.1, §4.

**Qué debes revisar:** Comprobar orden completo, quién verifica energía cero y requisitos de la excepción.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

