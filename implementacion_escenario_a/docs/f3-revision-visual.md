# Revisión técnica visual de extracción F3

Fecha: 2026-11-01. Revisor técnico: agente implementador Codex.
Alcance: 19 páginas de los 19 PDF, renderizadas con Poppler a 105 dpi.
No representa revisión académica ni autorización operativa.

Se inspeccionaron todas las imágenes de lectura. La revisión atendió límites de
filas/celdas, cabeceras partidas, cifras, unidades, condiciones y separación de anexos.
Las imágenes registradas se conservan en la evidencia F3 con SHA-256 del PDF y PNG,
comando y stderr. El verificador compara los PDF del host con los usados en Docker.

| Grupo inspeccionado | Contraste técnico observado |
| --- | --- |
| MAN-MTO-002 | Tablas de inventario/actividad y condición previa conservadas |
| MAN-OPE-001 | Fila de tramo multilínea unida sin desplazar longitud, diámetro, MAOP o caudal |
| MAN-OPE-004 | Cabecera «Periodicidad de verificación» reconstruida; signos ± conservados |
| PRO-HSE-003 | Secuencia completa y principio de energía cero conservados; principio como contexto |
| PRO-MED-007 v1/v2 | Tolerancias y reglas de escalamiento permanecen en su versión y tabla |
| PRO-OPE-012 v2/v3 | Umbral, ventana y nivel de alarma siguen en la fila y versión correspondientes |
| PRO-OPE-021 | Cinco pasos con acción y criterio íntegros; prerrequisitos y aborto como contexto |
| PRO-SEG-009/015 | Destinatario, plazo y responsable sin mezclar filas; reemplazo conservado |
| RES-ANH-0471 | Considerando conservado además de los artículos |
| RES-CREG-0112/0043 | Incertidumbre, periodicidad y derogatoria se conservan por artículo y documento |
| ACTA julio | Aprobación y condición de no exigibilidad permanecen juntas en §4 |
| ACTA noviembre | Manual no identificado sigue sin identificar; regla de certificación conservada |
| COM-PRV-0098 | Antecedente/recomendación/alcance separados; alcance acompaña recomendación |
| COM-PRV-0134 | Anexo separado y completo como dato no confiable; no se ejecutó su contenido |
| FIC-ACT-P101 | Columnas de diseño y alarma, tag P-101 e histórico conservados |

Poppler emitió avisos de fuentes Symbol/ArialUnicode; las páginas se renderizaron
y las viñetas y tablas se inspeccionaron en los PNG. No se modificaron los PDF ni
se instalaron fuentes globales. El aviso y el resultado de cada render se conservaron.

La revisión visual complementa 19 contrastes automáticos de encabezados y léxico
ordenado y las pruebas de filas críticas. No demuestra por sí sola relevancia de
una respuesta ni sustituye los quince casos académicos o el ataque de F9.
