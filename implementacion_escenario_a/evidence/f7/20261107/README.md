# Evidencia F7 en Docker dev

- [Suite de regresión](full/stdout-001.log), 178 pruebas aprobadas.
- [Construcción de la imagen](build-final/command.json),
  [preflight](preflight/stdout-001.log) y [plan F7](plan/stdout-001.log).
- [Validador de estructura y enlaces](validate/stdout-001.log).
- [Resumen de Inspector 2.13.0](inspector/summary.json) y
  [listado de las herramientas con esquemas](inspector/list/stdout-001.log).
  Corrida iniciada desde Windows PowerShell 5.1.26100.9711.
- [Repetición con docker.exe y lectura separada del resumen](powershell-separado.json)
  desde Windows PowerShell 5.1.26100.9711, con estado `passed`.
- [Búsqueda positiva](inspector/search-ok/stdout-001.log),
  [obtención positiva](inspector/direct-ok/stdout-001.log),
  [abstención](inspector/search-abstention/stdout-001.log) y
  [denegación](inspector/direct-denied/stdout-001.log).
- [Validación de entrada](inspector/privilege-invalid/stdout-001.log),
  [índice ausente](inspector/index-error/stdout-001.log) y
  [servicio no disponible](inspector/service-error/stdout-001.log).
- [Nueva sesión sobre Qdrant](inspector/reconnect/stdout-001.log),
  [negociación y stdout JSON-RPC](inspector/wire/stdout-001.log) y
  [diagnósticos separados](inspector/wire/stderr-001.log).
- [Obtención denegada en el volumen habitual](volumen/direct/stdout-001.log).
  Se ejecutó desde un directorio temporal distinto del proyecto. El resultado
  coincidió con la CLI F5 en el mismo contexto, salvo la correlación.

Las transcripciones registran comandos, estados, códigos de salida y
resultados estructurados. El ensayo histórico reconstruye el catálogo y
las proyecciones en temporales con las decisiones simuladas registradas.
[Guía de reproducción](../../../docs/validacion-dev-hasta-f7.md).
