# Análisis crítico — Escenario B

**Taller 2 · ARTI 4212**


Pregunta: ¿cuándo conviene el enfoque agéntico frente a la integración determinista en la gestión de una diferencia de balance volumétrico, y qué se decidió **no** agentizar?

---

## 1. Dónde conviene el enfoque agéntico

Un agente aporta cuando la tarea es abierta, exige correlacionar varias fuentes y su error se corrige aguas abajo. En este proceso hay tres puntos de ese tipo, todos de lectura y redacción:

- **Consultar procedimientos y normativa vigentes** para saber qué aplica al caso.
- **Formular la hipótesis de causa** cruzando inventario de línea, purgas, incertidumbre de medición y sustracción, con cita a documento, versión y sección.
- **Redactar la narrativa** del expediente, del borrador del acta y del reporte mensual.

El resto del proceso son reglas con consecuencia regulatoria y se resuelve de forma determinista: el cálculo de la cifra, las compuertas de 0,5 % y 1 %, el archivo automático, la **regla de sospecha de sustracción**, la consolidación mensual y el envío.

**Criterio usado:** se agentiza solo si (a) la tarea es abierta, (b) el error es tolerable porque hay revisión humana después, y (c) no produce una cifra ni una acción con efecto regulatorio. Si falla una de las tres, es determinista o humana.

Una consecuencia del criterio: el agente produce hipótesis, pero **cada una se verifica de forma determinista** (citas vigentes y cifras iguales a las del sistema de balance) antes de llegar al analista. Si la verificación falla dos veces, el agente se abstiene y el analista investiga a mano. El caso nunca se pierde.

---

## 2. Primera función que NO se agentizó: el cálculo de la diferencia

- **Mandato documental.** `PRO-MED-007 v2` §2.2 dice que el cálculo es determinista y que ningún otro sistema está autorizado a producir la cifra oficial.
- **Consecuencia regulatoria.** De la cifra dependen el escalamiento a Seguridad Física por encima del 1 % y el reporte mensual al regulador. Una aritmética no reproducible no se puede sustentar.
- **Sin valor agéntico.** El cálculo es cerrado. La incertidumbre está en explicar la causa, no en obtener el número.

En el BPMN, el cálculo está en el lane del **Sistema de balance** y no en el del agente. El agente solo lee la cifra ya calculada.

---

## 3. Segunda función que NO se agentizó: el envío del reporte al regulador

**Qué es.** La transmisión del reporte mensual consolidado (`RES-ANH-0471-2023` art. 2, dentro de 15 días calendario).

**Decisión.** El agente redacta el borrador y **no tiene herramienta ni credencial para enviar**. La Gerencia de Cumplimiento revisa y aprueba. Solo entonces una tarea determinista transmite el reporte aprobado a un destinatario fijado en configuración.

**Por qué.**

1. **Irreversible y de efecto externo.** Un reporte al regulador es una declaración oficial. No se deshace.
2. **Es el objetivo de un ataque.** `COM-PRV-0134` intenta que un sistema automático envíe el balance a un correo externo. Si el envío fuera una capacidad del agente, la inyección tendría un canal. Sin herramienta ni destino manejable por el agente, la instrucción es inejecutable.
3. **Rendición de cuentas.** Ante el regulador responde una persona con cargo, y el proceso exige su aprobación explícita.

**Otras decisiones no agénticas en el mismo punto:** el destinatario y los umbrales nunca se toman del texto recuperado, y las cifras del reporte se insertan desde el sistema de balance sin que el modelo las calcule ni las modifique.

---

## 4. Costos y límites del diseño

- **Poca autonomía por diseño.** Todo caso por encima de la tolerancia pasa por el analista, y todo reporte por Cumplimiento. Es el precio de que nada con valor regulatorio dependa de un modelo.
- **Mucha estructura alrededor de poco agente.** El modelo incluye verificación, reintentos, abstención, ruta manual y plazos. Es más complejo que un agente suelto, pero cada pieza responde a un modo de falla concreto.
- **Supuestos sin respaldo del corpus.** El modelo declara 30 (por ejemplo, la consecuencia del vencimiento de 3 días y el acuse del regulador). Son decisiones del grupo y quedan marcadas como tales.
- **Dependencia de la vigencia.** La verificación de citas supone saber qué documento está vigente. Hoy esa certificación la hace el área emisora a solicitud (`ACTA-CTO-2025-11` §4.2) y no existe como sistema. Si no existe un registro, la verificación tiene un límite de confianza que debe declararse.
- **Dónde reevaluar.** Si la evaluación del Escenario A muestra un anclaje alto y estable, se podría ampliar la autonomía en la investigación. Nunca en la cifra, la sospecha ni el envío.

**Conclusión.** En este problema domina lo determinista, porque casi todo son reglas con consecuencia regulatoria. El agente tiene lugar en explicar la causa y redactar, bajo verificación automática y aprobación humana.

---