# Evidencia de la revisión confirmada en Docker dev

La [autorización](../../../docs/revision/20261108-confirmada/autorizacion.md)
registra la revisión humana de Jonnathan Caballero del 8 de noviembre de 2026.
La [guía](../../../docs/validacion-dev-f11.md) permite repetir el contraste
de huellas y reconstruir las copias a partir de los catálogos archivados.

| Recibo | Resultado |
| --- | --- |
| [Registro de decisiones](registro/summary.json) | Laboratorio pasó de revisión 13 a 15. D01 y D02 están autorizados para lectura histórica en el grupo y ámbito aprobados. D03 sigue pendiente. Los controles de grupo, ámbito, uso y límite temporal niegan los demás accesos de estos manuales. Baseline conserva sus huellas. |
| [Propagación](propagacion/summary.json) | F10 publicó la revisión 15 y confirmó 15 eventos. El contexto habitual tiene cero documentos elegibles por su ámbito, grupo y uso. |
| [Lectura de manuales](lectura-manuales/summary.json) | Qdrant publicó 68 fragmentos de 14 documentos en un índice temporal autorizado. La obtención administrativa de D01 §2 y D02 §1 devolvió `encontrado` con las huellas esperadas. Baseline se verificó de nuevo tras la propagación. |
| [Fichas y copias aisladas](contextos/summary.json) | 24 casos congelados, 82 referencias y 43 fichas originales íntegras. Hay 24 catálogos y 25 contextos. R16 tiene rutas de índice separadas para auditoría y descarte. |
| [Regresión de gobierno](regresion.json) | 30 pruebas técnicas aprobadas en Docker. |

El [inventario de semillas](contextos/semillas-001.jsonl) incluye la huella del
catálogo y del contexto de cada caso. El [registro de aplicación](registro/decisions/)
contiene las dos decisiones efectivas exportadas. Los catálogos de los casos son
copias de preparación y sus índices se publicarán en la evaluación posterior.
