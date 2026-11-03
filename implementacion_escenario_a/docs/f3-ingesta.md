# F3: extracción PDF, partición y metadatos

Fecha: 2026-11-01, America/Bogota. Responsable técnico: Codex.
Estado: F3 técnica verificada en Docker `dev`. No se activaron índices ni consultas.

## Resultado y evidencia

En cada perfil, baseline y laboratorio: **19 documentos preparados, cero rechazados,
92 fragmentos y 92 padres**. Se reconstruyeron 15 tablas con 62 filas.
Máximo observado de entrada completa E5: **291 tokens**, frente al máximo 448.
La segunda preparación conserva generación, UUID y contenido, y reutiliza SQLite
sin insertar identidades adicionales. Los perfiles mantienen cuatro excluidos,
quince pendientes y cero certificados; revisión de gobierno 1 sin cambios.

- [Cierre técnico y copias verificadas](../evidence/f3/initial-20261101/closure-archived.json).
- [Baseline final: manifiesto, JSONL y reportes por PDF](../evidence/f3/initial-20261101/baseline-repeat/).
- [Segunda ejecución final](../evidence/f3/initial-20261101/baseline-reingest-final/).
- [Laboratorio final separado](../evidence/f3/initial-20261101/laboratorio-release/).
- [Copias SQLite de las generaciones finales](../evidence/f3/initial-20261101/stage-backups/).
- [120 pruebas aprobadas en dev](../evidence/f3/initial-20261101/tests-final/).
- [Validación final de estructura y fuentes](../evidence/f3/initial-20261101/validate-final/): máximo 194 líneas.
- [Renders con comandos y hashes](../evidence/f3/initial-20261101/render-recorded/)
  y [revisión visual técnica de las 19 páginas](f3-revision-visual.md).
- [Decisión de extracción y límites](adr-0007-extraccion-estructural.md).

La evidencia histórica y los PDF permanecen intactos. Las nuevas corridas se
ejecutaron en `reports/portable/f3-20261101` y se conservaron como evidencia F3.
El código local se usó mediante `dev`, sin reconstruir imagen ni cambiar dependencias.

## Interfaces construidas

| Módulo | Función |
| --- | --- |
| extract/pdf.py | PDF por página, secciones/artículos/anexo, parser 1.0.1 |
| extract/tables.py | Filas/cabeceras multilínea y trazas de líneas PDF; rechaza ambigüedades |
| extract/contrast.py | Contraste de encabezados y léxico ordenado, cifras, signos y unidades |
| extract/metadata.py | Ámbito observado separado del autorizado, gobierno nullable y relaciones |
| extract/prepare.py | Fragmentos con fuente, versiones, seguridad e input exacto de embedding |
| chunk/structural.py | UUID estables, padres, orden, partes, filas completas y conteo real |
| chunk/context.py | Prerrequisitos/principios/aborto y alcance de recomendaciones como contexto trazable |
| embeddings/input.py | Construcción compartida de input y tokenizador fijado, offline y verificado por hash |
| extract/staging.py | SQLite completo en temporal, consolidación y verificación de reingesta |
| extract/pipeline.py | Inventario completo: preparado o rechazado con causa por documento |

El texto de ingesta procede exclusivamente del PDF. Markdown solo detecta fallos;
no se usa para reconstruir, completar ni corregir una celda. Se conservaron por
documento el layout, secciones, tablas, fuentes por página/línea y resultado de contraste.
Cada línea JSONL contiene un registro íntegro; archivos divididos a 160 registros.

Los fragmentos reutilizan `Fragment` de F1. El envoltorio añade metadatos, input E5
exacto, huella del input y contexto común con sus fuentes. Para F4 debe usarse ese
input completo, verificándolo con `passage_input`, sin volver a concatenar o truncar.
El campo `documento.emisor` heredado de F2 representa el área emisora; el envoltorio
separa `area_emisora` y `emisor_documental`, ambos observados en el PDF.

## Integridad, tamaño y gobierno

Se mantiene `structural-es-1.0.0`: objetivo 250–350, máximo 448 incluyendo prefijo,
título, emisión, ámbito y contexto. Las 88 secciones breves quedan por debajo del
objetivo; cuatro están dentro. No se rellenan ni se mezclan secciones para aumentar
su tamaño. El solape adicional de prosa es cero, dentro del máximo de 40 acordado.

Las secciones de estos PDF caben íntegras. La división entre filas completas se
probó adicionalmente con una tabla sintética larga y el tokenizador real. Las
unidades indivisibles excedidas se rechazan sin truncar ni cortar una condición.
Las condiciones del acta de julio permanecen en §4; las secuencias conservan
prerrequisitos y aborto, y la recomendación del proveedor conserva su alcance.

El bundle E5, revisión y dimensiones no cambiaron. Sus cuatro archivos de
tokenizador se verifican contra huellas observadas en F0. No se descargaron modelos.
Gobierno, acceso y uso autorizado siguen viniendo de F2, nunca del texto ni de su
similitud. Los null de certificación/acceso no significan vigente o público.

COM-PRV-0134 y su anexo permanecen en los derivados; el anexo tiene sección, UUID,
procedencia y marca de instrucciones dirigidas al procesador. Todo contenido se
mantiene no confiable. Esto acredita conservación, no la prueba de ataque de F9.

Las generaciones SQLite viven en `artifacts/ingest/<perfil>/<generation_id>/`.
Son staging, con `index_revision=null`. No son un manifiesto activo de F4 ni un
registro nuevo de autorizaciones. F4 deberá rechazar una preparación con rechazos,
verificar coherencia y revalidar gobierno antes de publicar ambas proyecciones.

## Fallos conservados y controles

Las primeras pruebas detectaron celdas de un carácter, cabeceras multilínea y un
considerando ausente. Se corrigieron contra PDF. La inspección visual y el contraste
de títulos añadieron dos encabezados nominales del boletín, versionando parser a 1.0.1.
También se corrigió una comparación de tuplas Python frente a listas JSON en staging;
el intento fallido se conserva. Las corridas 1.0.0 son intermedias y no la entrega F3.

Las pruebas comprueban además pérdida de negación/signo, defecto de alineación,
celdas críticas, conservación del anexo, idempotencia y corrupción de payload.
En una copia aislada se alteró el Markdown de un documento: quedó con motivo de
revisión, cero fragmentos y salida de error; los originales no se tocaron.
Estas pruebas no sustituyen los quince casos académicos ni evalúan relevancia RAG.

## Repetir y continuar

Desde esta carpeta, elegir rutas nuevas de informes/pruebas:

```powershell
docker compose --profile dev run --rm dev -m petroandes.extract --profile baseline --output-dir reports/portable/f3-nueva-baseline
docker compose --profile dev run --rm dev -m petroandes.extract --profile laboratorio --output-dir reports/portable/f3-nueva-laboratorio
docker compose --profile dev run --rm dev -m pytest -q -p no:cacheprovider --basetemp artifacts/pytest-f3-nueva
```

El entrypoint ya es Python. La CLI rechaza sobrescribir evidencia; un PDF o catálogo
cambiado requiere revisar y registrar el cambio, no reutilizar aprobaciones.
Próximo paso técnico: F4, embeddings e índices persistentes coherentes por perfil.
Las decisiones académicas y los esperados de F1/F2 siguen pendientes.
