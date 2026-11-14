# Estado de reanudación

Actualizado el 2026-11-13, America/Bogota. Responsable técnico Codex.

La presentación usa una sola conexión `petroandes` en Inspector y VS Code.
`python -m petroandes.demo` prepara una copia privada del snapshot aprobado
de revisión 15: 14 documentos y 68 fragmentos, con reloj histórico explícito
del 8 de noviembre. Se mantienen exclusiones, documento pendiente y descarte
del anexo. [ADR 0013](adr-0013-mcp-demostracion-unica.md).

En Docker `dev` aprobaron nueve llamadas SDK, las comprobaciones con Inspector
real y las 180 pruebas de regresión. Baseline conserva revisión 1. Inspector
web está disponible en 6274. Copilot confirmó incertidumbre 0,3 % en revisión 15.
Los tres Word se actualizaron y revisaron visualmente, con 4, 4 y 5 páginas.
[Evidencia actual](../evidence/f7/20261112-demo-unica/README.md) ·
[Inspector](inspector-web.md) · [Copilot y prompts](copilot-vscode.md).
Se añadió el [Word de patrones EIP](../../output/doc/Patrones_Arquitectura_EIP_PetroAndes.docx)
con diagrama integral e iconos oficiales atribuidos. Sus cuatro páginas se
renderizaron y revisaron. [Recibo](../evidence/f11/20261112-eip-documento/summary.json).
El 13 de noviembre se documentó el [diseño de seguridad y la contención F9](../../output/doc/Diseno_Seguridad_y_Contencion_Ataque_PetroAndes.docx).
El Word de tres páginas explica recuperación, descarte F6 y límites de la
regla de anexos; utiliza la evidencia archivada sin ejecutar otra corrida.
Se contrastaron las sesiones 13 y 14 con F9 y fuentes de industria. La
[propuesta de mejora](propuesta-f9-clases-13-14-20261113.md) está preparada, sin cambios de implementación.
Las conexiones y recibos descritos a continuación corresponden al historial;
la configuración de presentación actual reemplaza esos nombres anteriores.

El 11 de noviembre se comprobó `petroandes-historico-f7` con Inspector
2.13.0 en el servicio web activo. Listó las dos herramientas y devolvió
la presión de diseño y alarma de P-101, además del artículo 2 de la
resolución de incertidumbre. La página local respondió HTTP 200 en 6274.
[Recibo de disponibilidad](../evidence/f7/20261111-disponibilidad/summary.json).

En VS Code el servidor histórico aparecía en `Error`. Al ejecutar
`Start Server` pasó a `Running`. Un chat nuevo de Copilot llamó a la
herramienta de ese servidor y recibió el límite de incertidumbre de 0,3 %.
[Validación desde VS Code](../evidence/f7/20261111-vscode/conexion.md).

## Tarea activa

F11 prepara la entrega técnica reproducible. La guía arranca desde Docker
`dev` con un proyecto aislado, descarga las revisiones fijadas, reconstruye
el baseline desde PDF y ejecuta la regresión y los controles F7 a F10. La
corrida parte de artefactos ausentes y produce recibos, informes por etapa,
inventario de entrega y licencias declaradas. Conserva la evaluación
diagnóstica separada de la evaluación formal.
[Validación F11](validacion-dev-f11.md) · [Resultados y pendientes](f11-resultados.md) ·
[Correspondencia ADR y EIP](f11-diseno-eip.md) · [Evidencia F11](../evidence/f11/20261108/).
La [guía de entrega](entrega-tecnica.md) explica el ZIP, su huella SHA-256
y cómo comprobar una copia extraída con el perfil Docker `dev`.

## Implementación anterior F10

F10 consolida desde los PDF y propaga cambios del catálogo bajo demanda. El
consumidor confirma el outbox después de verificar y activar las tres
proyecciones. Si se interrumpe antes de confirmar, el reintento reutiliza la
generación completa. Las entradas E5 idénticas reutilizan sus vectores y la
reversión comprueba revisión, contexto y elegibilidad del catálogo vigente.

En Docker `dev`, el ensayo histórico pasó de la revisión 13 a la 17 sobre
copias temporales. Partió de 19 documentos y 58 fragmentos publicados y
terminó sin eventos pendientes. Demostró vencimiento, revocación durante
consulta con el vector anterior presente, reaprobación, cambio de permisos,
cambio de hash y recuperación de fallos. Reconstruyó una colección con el
bundle y la partición fijados y comprobó la reversión segura.
La regresión completa aprobó 180 pruebas y la CLI confirmó el replay sin staging.
[Validación hasta F10](validacion-dev-f10.md) · [Operación](f10-operacion.md) ·
[Evidencia F10](../evidence/f10/20261108/).

## Implementación anterior F9

F9 verifica la contención del anexo de COM-PRV-0134 en una copia temporal de
laboratorio. En Docker `dev`, F5 recuperó el anexo íntegro de la página 1 y F6
registró su descarte antes de abstenerse. Inspector 2.13.0 devolvió los mismos
resultados que Python para el ataque, la lectura de auditoría y la consulta
legítima de firmware 7.4. Las consultas conservaron el catálogo en revisión
13 con la misma huella y no activaron los observadores de efectos. Se reutilizó
la decisión académica existente para inspección como dato no confiable.
El ensayo aprobó las 19 comprobaciones y la suite de regresión aprobó 178 pruebas.
[Validación hasta F9 en Docker dev](validacion-dev-f9.md) ·
[Evidencia F9](../evidence/f9/20261108/).

## Implementación anterior F8

F8 incorpora un arnés técnico que registra resultados Python/MCP, trazas,
procedencia y métricas diagnósticas con laya multilingüe. Usa cuatro controles
del laboratorio en una copia aislada. La captura termina y libera E5 antes
de iniciar los juicios de laya. En Docker dev hubo paridad en 4 de 4 llamadas,
respaldo de 2 de 2 afirmaciones y 3 de 9 candidatos marcados como pertinentes.
[Validación de F8 en Docker dev](validacion-dev-f8.md) · [ADR del evaluador](adr-0012-evaluacion-f8.md) ·
[Evidencia F8](../evidence/f8/20261108/).

## Implementación anterior F7

F7 conecta `buscar_documentos` a F6 y `obtener_fragmento` al acceso directo F5.
El punto de entrada es `python -m petroandes.mcp_server --profile PERFIL`.
Publica esquemas de entrada y salida a partir de los contratos de F1.
El perfil y el contexto se resuelven en el despliegue. El protocolo stdio
reserva stdout y lleva diagnósticos a stderr.

[Contratos MCP](f7-mcp.md) · [Guía hasta F7 en Docker dev](validacion-dev-hasta-f7.md) ·
[Evidencia F7](../evidence/f7/20261107/).

Imagen construida y 178 pruebas de regresión aprobadas en `dev`. Inspector
2.13.0 con SDK Python 1.30.0 verificó las dos herramientas, los retornos
positivos y negativos y el rechazo de parámetros inválidos. La sonda stdio
negoció 2025-11-25 y confirmó que los diagnósticos llegan a stderr.
La reconexión recuperó la misma generación con 58 puntos y los resultados
coincidieron con las funciones Python salvo la correlación. En el volumen
habitual, la denegación coincidió con la CLI desde otro directorio.

El perfil `inspector` incorpora el Inspector web en `127.0.0.1:6274`. La
conexión desde el navegador negoció MCP `2025-11-25` y ejecutó ambas
herramientas con la revisión 13 de laboratorio. La API respondió `401` sin
token. [Guía web](inspector-web.md) · [ADR de despliegue](adr-0011-inspector-web.md) ·
[Evidencia web](../evidence/f7/20261108/inspector-web.md).

Las conexiones `petroandes` y `petroandes-historico-f7` aparecen en el mismo
Inspector del puerto 6274. Se probaron en el navegador los cuatro casos con
la revisión 13. Para pasar de P-101 a la resolución, los argumentos JSON
evitan conservar un filtro `activo` vacío. La
[guía de laboratorio](../../output/doc/Guia_Laboratorio_MCP_Inspector_PetroAndes.docx)
recoge la secuencia y los resultados. [Evidencia del Inspector unificado](../evidence/f7/20261108/inspector-unificado.md).

La [práctica con Copilot en VS Code](copilot-vscode.md) añade dos conexiones
de espacio de trabajo y cuatro prompts de demostración. Los prompts eligen
el contexto habitual o histórico según el caso y llaman a las herramientas
MCP de Docker dev por stdio. Se observaron las cuatro llamadas en el chat
Local con los servidores y resultados esperados. [Evidencia de Copilot](../evidence/f7/20261108/copilot-vscode.md).
La guía incluye las cuatro preguntas en lenguaje natural para el chat Local.
El caso 3 se probó también como pregunta libre y devolvió la cita de la ficha.

## Implementación anterior F6

F6 implementa composición extractiva determinista sobre la recuperación F5.
La operación `responder` de `tools/f5.py` devuelve `SearchResponse`, una
representación legible y una traza correlacionada. El conjunto autorizado y
la revisión se verifican después de componer, antes de devolver la respuesta.

[ADR de composición](adr-0010-composicion-f6.md) ·
[Guía de validación en Docker dev](validacion-dev-hasta-f6.md) ·
[Evidencia de F6](../evidence/f6/20261107/).

La imagen se construyó y la suite completa pasó 178 pruebas en Docker `dev`,
incluidos 22 controles de F6. Los comandos de la guía se probaron en
Windows PowerShell 5.1.

Las reglas conservan condiciones, cifras, negaciones y citas por afirmación.
Exigen ámbito para las filas de tramo o activo, anclas documentales y
secciones completas. Distinguen alarma, MAOP, especificación de activo,
incertidumbre, tolerancia, secuencia, recomendación y decisiones históricas.
La traza identifica el anexo descartado y la obtención autorizada conserva
su texto marcado como no confiable.

La prueba histórica parte de la revisión 13. Reingiere los 19 PDF y reabre
58 fragmentos de 12 documentos bajo `LAB_REVISION`, `general:corpus_revision`
y `evidencia_historica`, con el reloj controlado dentro del período aprobado.
Verifica extractos positivos, ámbito ambiguo, evidencia insuficiente,
datos fuera del corpus, conflicto y vencimiento durante la composición.
El ensayo histórico de MAOP usó el extractor de filas en aislamiento.
La certificación simulada posterior de MAN-OPE-001 se registra en la revisión 15.

## Estado del despliegue y continuidad

| Perfil | Revisión | Clasificación | Respuesta en el contexto del servicio |
| --- | --- | --- | --- |
| baseline | 1 | 4 excluidos, 15 pendientes | `sin_evidencia_autorizada` |
| laboratorio | 15 | 4 excluidos, 1 pendiente, 14 certificados simulados | `sin_evidencia_autorizada` |

El contexto del servicio usa grupo `lectores-educativos`, ámbito
`general:lectura-documental-educativa` y uso `recomendacion`. Las
certificaciones simuladas tienen ámbito `general:corpus_revision`,
grupo `LAB_REVISION` y fin exclusivo 2026-12-01T00:00:00-05:00.
La obtención directa de la ficha P-101 en el contexto del servicio
devuelve `evidencia_no_autorizada`.

El [estado hasta F5](estado-hasta-f5.md) conserva el historial y las evidencias
de F0 a F5 y de la [incorporación administrativa](certificacion-laboratorio-20261103.md).
Incluye la corrección de reapertura de Qdrant y la CLI compatible con
Windows PowerShell. La guía anterior conserva las comprobaciones de
catálogo, publicación y recuperación de candidatos.
[Validación hasta F5](validacion-dev-hasta-f5.md).

## Revisión confirmada y siguiente fase

- Jonnathan Caballero aprobó las 24 fichas el 8 de noviembre de 2026.
  La [matriz versionada](revision/20261108-confirmada/matriz.md) conserva
  17 esperados y aplica las siete correcciones acordadas. El manifiesto
  congela ocho casos de ajuste y dieciséis de reserva.
- D01 (MAN-MTO-002 v1) y D02 (MAN-OPE-001 v3) tienen permiso simulado de
  lectura histórica. D03 (MAN-OPE-004 v2) sigue pendiente. F10 publicó la
  revisión 15 y confirmó 15 eventos para el contexto habitual del servicio.
- Docker `dev` comprobó 82 referencias a PDF, las 43 fichas originales y
  24 copias aisladas con 25 contextos. Los dos contextos de R16 permiten
  comprobar por separado auditoría y descarte. [Evidencia](../evidence/revision/20261108-confirmada/README.md).
- La evaluación formal sigue pendiente. El siguiente paso es publicar los
  índices de prueba, calibrar con ajuste y evaluar la reserva con sus métricas
  y denominadores. La sustentación breve corresponde al estudiante.
