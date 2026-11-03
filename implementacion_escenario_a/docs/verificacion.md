# Verificación del paquete del agente

Fecha: 2026-11-01. Esto valida la preparación del agente, no la aplicación 3.2.

## Comprobaciones realizadas

- Estructura, JSON, TOML, sintaxis Python, enlaces y límite de líneas validados
  mediante `tools/validate_agent.py`.
- Tres habilidades aceptadas por `quick_validate.py` de Skill Creator.
  La dependencia PyYAML 6.0.3 del validador se usó en un directorio temporal;
  las herramientas entregadas no requieren PyYAML ni paquetes adicionales.
- Siete fuentes originales presentes con SHA-256 coincidente.
- Corpus de 19 PDF y 19 Markdown emparejados por ruta y nombre; esto no
  demuestra igualdad de contenido ni sustituye la extracción PDF de F3.
- Lector probado sobre Word y Markdown, sección F0, ID inexistente, intento
  de ruta externa y advertencia ante hash diferente, sin modificar originales.
- Evaluación independiente de arranque con instrucciones y habilidad de desarrollo.
  Los hallazgos de inventario se incorporaron al preflight.

## Entorno observado

Se usó Python 3.12.14 del runtime disponible para esta verificación.
Se detectaron pypdf 6.10.0 y Pydantic 2.14.1. Las demás dependencias de la
aplicación no estaban detectadas en ese intérprete. Node del PATH fue v20.19.4,
inferior al mínimo 22.19.0 de la documentación de Inspector consultada.
El preflight ahora informa estas advertencias; no modifica el sistema.
El intérprete y PATH de VS Code pueden ser distintos y deben comprobarse allí.

## Pendiente al iniciar F0

Preparar entorno aislado, fijar versiones compatibles y ejecutar pruebas reales
de Qdrant, E5, laya e Inspector. No se descargaron modelos ni se implementó el
servicio como parte de la preparación del agente. No se comprobó una sesión
real de VS Code ni su configuración efectiva; seguir README e INICIO allí.
