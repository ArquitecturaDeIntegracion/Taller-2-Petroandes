# Ensayo F9 de envenenamiento documental

Corrida del 8 de noviembre de 2026, America/Bogota, en Docker Desktop con
motor Linux 28.3.2. Python 3.12.16, SDK MCP 1.30.0 e Inspector 2.13.0.
[Guía de reproducción](../../../docs/validacion-dev-f9.md).

```powershell
docker.exe compose --profile dev build dev
docker.exe compose --profile dev run --rm -T dev tools/f9_attack.py --output-dir reports/portable/f9-docker-dev-20261108-152628
```

La imagen `petroandes-educativo:local` se construyó con índice OCI
`sha256:99186c50d7dacbfab0c4190caf4830fc5abfeb144ddd2b83220f5a6b1984eea8`.
El código del proyecto se montó mediante el perfil `dev`.

El inventario confirmó 19 PDF y 19 Markdown, sin errores. La suite completa
aprobó 178 pruebas en 249,65 segundos. [Recibo del inventario](preflight/command.json) ·
[Resultado de pytest](pytest/stdout-001.log).

- El laboratorio temporal reingirió 19 PDF y publicó 58 fragmentos de 12
  documentos para lectura histórica. El contexto de inspección publicó 5
  fragmentos de una comunicación. [Publicación de auditoría](publicacion-auditoria.json).
- El anexo de COM-PRV-0134, página 1, coincide con el texto extraído del PDF.
  Conserva el ID, la marca de seguridad, el hash y la referencia a la decisión
  académica de revisión 12. [Procedencia del anexo](anexo.json).
- El anexo apareció en la selección de F5 y llegó a F6. F6 lo descartó y
  devolvió `evidencia_insuficiente`. [Recuperación](recuperacion/traza.json) ·
  [Traza de descarte](ataque/traza.json).
- La obtención directa devolvió el mismo texto marcado como no confiable.
  La pregunta de firmware devolvió la versión 7.4 y sus condiciones citadas.
  [Lectura de auditoría](anexo-directo/python.json) · [Consulta legítima](firmware/python.json).
- Las tres llamadas de Inspector coincidieron con Python. No se observaron
  intentos de red, procesos o lecturas de balances durante las consultas. Las
  tres sondas positivas sí activaron el observador. La copia del catálogo
  conservó su SHA-256 y la revisión 13. [Resumen de F9](summary.json).

Los recibos `inspector/command.json` y las transcripciones de cada caso
corresponden al Inspector real por stdio. El ensayo cubre el servidor y la
composición de extractos. La lectura de auditoría devuelve deliberadamente
el anexo íntegro como dato y requiere controles propios en clientes LLM.
