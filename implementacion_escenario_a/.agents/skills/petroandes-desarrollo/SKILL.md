---
name: petroandes-desarrollo
description: Desarrolla los módulos Python del Escenario A de PetroAndes siguiendo F0 a F4 y F10 del plan, incluidos entorno, gobierno, ingesta PDF e índices Qdrant. Úsala para iniciar o continuar esa implementación educativa.
---

# Desarrollo modular de PetroAndes

## Contexto mínimo

La raíz de implementación contiene AGENTS.md, knowledge y tools.
Localízala desde el cwd o la ubicación de esta habilidad, sin suponer rutas de usuario.
Lee su AGENTS.md y docs/estado.md si aún no están en contexto.
Consulta knowledge/03-arquitectura.md y knowledge/02-gobierno.md según el módulo.

## Procedimiento

1. Identifica la tarea activa y los artefactos existentes antes de crear código.
2. Lee solo la fase necesaria: desde la raíz de implementación, ejecuta
   `python tools/read_source.py plan --section "F0 Preparación"`, sustituyendo
   el título cuando avances. Consulta actividad o teoría ante dudas del contrato.
3. En F0, ejecuta las herramientas de inventario y luego las pruebas reales de
   modelos, almacenamiento y MCP. Inventariar no demuestra compatibilidad.
4. Implementa un módulo con entradas, salidas y fallos explícitos; conserva los
   contratos y decisiones versionadas del proyecto.
5. Valida el comportamiento con evidencia concreta y actualiza docs/estado.md.

## Decisiones que cambian el desarrollo

- Los 19 PDF son la ingesta; los resúmenes o Markdown no los sustituyen.
- La evidencia del corpus y las decisiones académicas revisadas se separan.
- ID, hash y ubicación deben seguir siendo trazables tras partición y reingesta.
- El bundle E5 se fija exactamente como en 3.1, sin mezclar espacios vectoriales.
- Qdrant local tiene un único propietario; no usar snapshots nativos ni abrir
  la misma carpeta desde varios procesos.
- Publicar una generación completa, con fragmentos y proyecciones coherentes.
- La revocación gobierna la consulta aunque permanezca un vector antiguo.
- Mantener archivos de texto de máximo 200 líneas y evitar arquitectura adicional.

Si falta una decisión humana, prepara la propuesta y continúa lo independiente.
No fabricar aprobación ni reemplazar una dependencia fallida silenciosamente.
Para búsquedas o herramientas MCP usa petroandes-recuperacion-mcp; para casos,
métricas, ataque o cierre usa petroandes-evaluacion cuando estén disponibles.
