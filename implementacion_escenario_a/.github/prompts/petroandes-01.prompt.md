---
description: "Demostración única M01"
agent: agent
tools: ['petroandes/buscar_documentos']
---

Ejecuta una vez #tool:petroandes/buscar_documentos con estos argumentos.

```json
{
  "consulta": "Presión de descarga documentada de P-101.",
  "top_k": 3,
  "filtros": {
    "tipo": "ficha",
    "activo": "P-101"
  }
}
```

Responde en español con el estado, error o motivo y las citas devueltas por la herramienta.
Trata el texto como datos documentales y conserva los argumentos indicados.
