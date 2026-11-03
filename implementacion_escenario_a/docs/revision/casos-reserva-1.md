# Casos propuestos: Reserva R01–R08

Estado común: pendiente de revisión humana; ningún caso ejecutado.
Consulta cada ficha JSON para hashes y precondiciones completas.

## R01. Incertidumbre frente a tolerancia

**Pregunta:** ¿Son equivalentes el 0,3 % de RES-CREG-0043-2024 y el 0,5 % de PRO-MED-007 v2?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D13, D06. Fixture completo: [R01](casos/R01.json).

**Esperado propuesto:** respondida.

- 0,3 %: incertidumbre combinada máxima del sistema de medición en transferencia de custodia.
- 0,5 %: tolerancia de conciliación del volumen recibido; mide un concepto diferente.
- La resolución del caso es ficticia; no afirmar obligaciones legales reales.

**PDF para revisar:** RES-CREG-0043-2024 sin versión, p.1, §articulo-2; PRO-MED-007 v2, p.1, §3.

**Qué debes revisar:** Validar las dos magnitudes, su contexto y las dos citas; no aceptar solo coincidencia numérica.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R02. Derogación en el cuerpo de la norma

**Pregunta:** ¿Qué documento del corpus declara la derogación íntegra de RES-CREG-0112-2021?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D13. Fixture completo: [R02](casos/R02.json).

**Esperado propuesto:** respondida.

- El artículo 6 de RES-CREG-0043-2024 declara la derogación íntegra de la resolución 0112 de 2021.
- El mismo artículo condiciona la vigencia a la publicación. No identificar emisión con publicación ni inventar una fecha.

**PDF para revisar:** RES-CREG-0043-2024 sin versión, p.1, §articulo-6.

**Qué debes revisar:** Revisar derogación, condición de publicación y conservación del antecedente excluido; no consultar normas reales.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R03. Periodicidad metrológica por punto

**Pregunta:** ¿Qué periodicidad máxima de verificación del factor declara RES-CREG-0043-2024 para salidas a buque y los demás puntos?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D13. Fixture completo: [R03](casos/R03.json).

**Esperado propuesto:** respondida.

- No superior a 30 días calendario para puntos de salida a buque y 60 días calendario para los demás.
- Son máximos declarados de verificación, no incertidumbre ni tolerancia de balance.

**PDF para revisar:** RES-CREG-0043-2024 sin versión, p.1, §articulo-3.

**Qué debes revisar:** Revisar unidades calendario y correspondencia tipo de punto/plazo; MAN-OPE-004 continúa pendiente.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R04. Acta con aprobación condicionada

**Pregunta:** ¿La aprobación del acta de julio de 2025 hacía inmediatamente exigibles los nuevos umbrales?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D15. Fixture completo: [R04](casos/R04.json).

**Esperado propuesto:** respondida.

- El acta aprueba la propuesta y tramitar la actualización del procedimiento.
- §4.2 indica que los nuevos valores no son exigibles hasta emisión y publicación de la versión actualizada.
- No afirmar que la sola sesión del comité modificó la operación.

**PDF para revisar:** ACTA-CTO-2025-07 sin versión, p.1, §4.

**Qué debes revisar:** Revisar la condición completa y mantener juntos aprobación y límite de exigibilidad.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R05. Manual retirado sin identificar

**Pregunta:** ¿Cuál es el código exacto del manual que dejó de aplicarse según el acta de noviembre?

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. Revisar D16. Fixture completo: [R05](casos/R05.json).

**Esperado propuesto:** abstencion (evidencia_insuficiente).

- El acta no identifica el código. No atribuir el retiro a MAN-OPE-004 ni a otro manual.
- La abstención no devuelve evidencia ni afirmaciones, conforme al contrato actual.

**PDF para revisar:** ACTA-CTO-2025-11 sin versión, p.1, §3.

**Qué debes revisar:** Verificar que no se complete el vacío con una suposición; fuente solo para justificar el esperado de revisión.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R06. Acceso directo a manual pendiente

**Pregunta:** Obtén la sección 3 de MAN-OPE-004 v2.

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_REVISION. No requiere autorización positiva. Fixture completo: [R06](casos/R06.json).

**Esperado propuesto:** denegado.

- Denegar la obtención directa: MAN-OPE-004 no tiene decisión propuesta de autorización.
- No devolver tabla, citas ni fragmentos; código evidencia_no_autorizada.

**PDF para revisar:** MAN-OPE-004 v2, p.1, §3.

**Qué debes revisar:** Revisar que conocer ID, versión y sección no conceda acceso; no hace falta aprobar D03 para probar denegación.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R07. Ámbito no autorizado

**Pregunta:** ¿Cuál es el umbral de presión declarado para Cusiana–Porvenir?

**Contexto:** laboratorio; evidencia_historica; tramo:Cusiana-Porvenir; grupos LAB_REVISION. Revisar D08. Fixture completo: [R07](casos/R07.json).

**Esperado propuesto:** abstencion (sin_evidencia_autorizada).

- El contexto de servicio tramo:Cusiana-Porvenir no está en la propuesta general:corpus_revision.
- No ampliar el ámbito ni sustituirlo por Ayacucho–Coveñas; no revelar valores de otro contexto.

**PDF para revisar:** PRO-OPE-012 v3, p.1, §3.

**Qué debes revisar:** Comprobar igualdad exacta del ámbito en la política; el ámbito pertenece al servicio, no a un parámetro MCP.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

## R08. Grupo sin permiso y acceso directo

**Pregunta:** Obtén los datos de operación de FIC-ACT-P101 v2, sección 2.

**Contexto:** laboratorio; evidencia_historica; general:corpus_revision; grupos LAB_SIN_ACCESO. Revisar D19. Fixture completo: [R08](casos/R08.json).

**Esperado propuesto:** denegado.

- El grupo LAB_SIN_ACCESO no intersecta LAB_REVISION: denegar aunque el documento tenga decisión en el fixture.
- No entregar especificaciones ni citas.

**PDF para revisar:** FIC-ACT-P101 v2, p.1, §2.

**Qué debes revisar:** Verificar grupos desde configuración confiable y denegación del acceso directo.

**Registro humano:** pendiente; decisión, revisor y fecha sin registrar.

