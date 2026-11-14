# ADR 0014 Contención verificable en el arnés F9

Fecha: 2026-11-13. Aceptado para el laboratorio por la solicitud de implementación.
Referencia: [análisis de las clases y propuesta](propuesta-f9-clases-13-14-20261113.md).

## Decisión y alcance

F9.1 amplía las pruebas de seguridad del Escenario A. Conserva la prueba F9,
el compositor extractivo, E5, Qdrant, laya y la conexión pública `petroandes`.
No cambia permisos aprobados ni usa la reserva formal para ajustar el sistema.
El ejecutor nuevo pertenece al ensayo del consumidor; no se inserta en Copilot
ni limita otras herramientas o permisos del IDE.

Se integran tres fases independientes mediante `tools/f9_guard_check.py`:

1. F9 original con PDF, recuperación E5/BM25, descarte F6 e Inspector real.
2. Fronteras MCP reales en dos contextos privados de un snapshot histórico.
3. Cliente determinista, casos sintéticos nuevos y dispatcher de plan fijo.

El segundo y tercer bloque no son servidores adicionales de presentación.
Los índices privados y los contextos del ensayo terminan con el proceso.

## Política del consumidor de prueba

El código fija identidad, uso, objetos, herramientas y presupuesto antes de
entregar al cliente un fragmento no confiable. El cliente propone acciones
declaradas por el fixture y conserva recibos de exposición con procedencia,
sesión y SHA-256. No decide mediante un LLM ni detecta intención semántica.

El dispatcher valida el esquema completo y la lista permitida, después
objeto e identidad, referencia documental y hash. Solo ejecuta dobles de
lectura sobre datos ficticios. Correo, shell, lectura de archivos arbitrarios
y cambios de permisos carecen de implementación y se rechazan explícitamente.
El borrador sintético solo se acepta si reproduce el extracto autorizado.
Esta comprobación no sustituye el compositor real ni el evaluador laya.

## Aislamiento y evidencia

`f9-sandbox`, dentro del perfil Docker `dev`, usa UID 10001, raíz de solo
lectura, capacidades vacías, no-new-privileges, red none, temporal acotado
y límites de CPU, memoria y procesos. Solo monta fuente RO, pesos RO y la
carpeta de esta corrida RW en `/f9-output`. Los reportes anteriores siguen RO.
No monta artifacts persistentes ni el socket Docker.

El controlador del host crea un receptor ficticio en una red Docker interna.
Una sonda libc lo alcanza desde el control positivo; otra intenta alcanzar
el mismo destino desde el sandbox. Se inspeccionan configuración efectiva y
restricciones del proceso. Los recursos se identifican con UUID y etiqueta
propia; la limpieza verifica esa etiqueta antes de eliminarlos.

Los resultados distinguen exposición, propuesta, denegación, lectura autorizada,
filtración, contaminación, errores e inconclusos. Los controles benignos
verifican utilidad del dispatcher sintético. No miden falsos positivos de F6.
Faltantes, errores o timeout no acreditan contención. Cada ejecución crea
evidencia nueva sin sobrescribir anteriores.

## Consecuencias y límites

La regla de anexos de F6 sigue siendo una referencia determinista y limitada.
Las variantes Unicode, tablas y base64 prueban la frontera del consumidor,
mediante propuestas forzadas; no prueban cobertura del recuperador o detector.
El cliente LLM real queda `no_evaluado`. No se añade detector universal,
autenticación productiva, durabilidad automática, OT ni Escenario B.
Docker reduce acceso y salida de red del worker; no garantiza inmunidad a
escapes de contenedor ni prohíbe todos los subprocess del mismo usuario.

[Operación y validación](validacion-dev-f9-1.md).
