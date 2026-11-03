# Evidencia F4 en Docker dev

Fecha de trabajo local: 2026-11-01, America/Bogota; recibos con hora UTC.

- `validate-start`, `preflight-start`, `plan`: arranque y lectura delimitada de F4.
- `audit-run`, `audit/`: inferencia E5 real de 92 fragmentos, NPY sin pickle,
  mapa de filas/UUID/hash, bundle, medidas por lote y resumen.
- `tests-initial`: primeras cinco pruebas F4; advertencia por caché pytest de solo lectura.
- `tests-full`: 125 pruebas en el incremento intermedio, sin advertencias.
- `tests-final`: 134 pruebas aprobadas, incluido el incremento de integridad.
- `baseline-run`, `laboratorio-run`: publicación real de cero fragmentos elegibles.
- `baseline-reopen-run`: reapertura en otro contenedor.
- `baseline-repeat-run`, `laboratorio-repeat-run`: misma generación/colección, sin duplicados.
- `closure-run`, `closure/`: verificación real de perfiles y auditoría, exportación
  de manifiestos/recibos y copias SQLite de las ramas y del registro de publicaciones.
- `implementation-sha256.json`: hashes calculados del código y documentos de este incremento.
- `validate-final`: validación de sintaxis, formatos, enlaces, fuentes y límite de líneas.
- `validate-prearchive`: intento que detectó el enlace al informe aún sin archivar;
  se conservó y se corrigió creando el destino antes de la validación final.

Los `command.json` contienen argv, cwd portable, hora, duración, código observado
y referencias a stdout/stderr en partes de hasta 160 líneas.
El perfil dev monta el código local de solo lectura; modelos y artefactos están
en volúmenes persistentes. No se reconstruyó la imagen ni cambiaron dependencias.

La auditoría conserva todos los fragmentos F3. No es un índice consultable ni
una autorización. Gobierno real: cuatro excluidos, quince pendientes, cero
certificados por perfil, revisión 1. Las propuestas académicas no se importaron.
Las pruebas positivas no vacías usan datos/decisiones ficticios en temporales;
la persistencia no vacía se verifica mediante un proceso hijo independiente.

No se copiaron directorios Qdrant abiertos ni se usaron snapshots nativos.
La recuperación del índice se basa en reconstrucción desde PDF, F3 y gobierno.
Se conservaron todos los recibos iniciales y la evidencia anterior del taller.

Ver [informe técnico](../../../docs/f4-indices.md),
[ADR](../../../docs/adr-0008-publicacion-f4.md) y
[cierre](closure/closure.json).
