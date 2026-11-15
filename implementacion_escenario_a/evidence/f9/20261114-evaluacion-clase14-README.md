# Evaluación documental del arnés y la clase 14

Fecha de cierre: 14 de noviembre de 2026, America/Bogota.

El [informe Word](../../../output/doc/Informe_Evaluacion_Arnes_Clase14_PetroAndes.docx)
tiene cuatro páginas y dos diagramas originales. Explica la implementación,
contrasta la clase 14 y fuentes primarias de industria e investigación, y
separa los hallazgos actuales de las mejoras propuestas.

## Hallazgos

- El filtro F6 usa `anexo-*` y una marca estructural; no detecta intención.
- La prueba original recupera el ataque real y registra el descarte en F6.
- El dispatcher y su plan fijo operan sobre un consumidor determinista y dobles.
- El aislamiento Docker limita el worker del ensayo, no las capacidades del IDE.
- Las llamadas MCP normales no persisten automáticamente la traza F9.
- La reserva formal y un cliente LLM real no se evaluaron en esta revisión.

La propuesta prioriza contener el consumidor real, registrar cada consulta,
ampliar las señales de detección y probar el flujo desplegado con nuevos PDF.
Se conserva la composición extractiva y el original envenenado.

## Alcance de la comprobación

Se revisaron código, diapositivas y evidencia archivada de Docker dev del
13 de noviembre. Los 19 archivos técnicos del manifiesto F9 mantienen sus
hashes. No se declara una nueva ejecución Docker ni una mejora implementada.
El preflight del host no reportó errores; advirtió Node 20.19.4 frente al
mínimo 22.19.0 de Inspector. Esa comprobación no sustituye la evidencia Docker.

[Recibo y huella del Word](20261114-evaluacion-clase14/summary.json) ·
[Fuentes locales](20261114-evaluacion-clase14/fuentes-locales.jsonl) ·
[Fuentes externas](20261114-evaluacion-clase14/fuentes-externas.json).
