# Evidencia F5 en Docker dev

- [Construcción](build-verified/command.json), [preflight](preflight/stdout-001.log)
  y [plan F5](plan/stdout-001.log).
- [Suite completa en Docker dev](full-verified/stdout-001.log) con 156 pruebas aprobadas.
- [Ensayos con trazas](targeted-verified/stdout-001.log). El ensayo histórico
  reingirió 19 PDF, reabrió la publicación de 58 fragmentos de 12 documentos
  con permisos simulados y comparó resultados densos, léxicos y fusionados.
  El ensayo sintético registra el filtro de la llamada real a Qdrant.
- [Fallo de reapertura reproducido antes de corregir la huella](corpus-reopen/stdout-001.log).
- [Catálogo baseline](baseline-state/stdout-001.log) y
  [abstención baseline](baseline-search/stdout-001.log).
- [Catálogo laboratorio](lab-state/stdout-001.log),
  [abstención laboratorio](lab-search/stdout-001.log),
  [obtención denegada](lab-direct-verified/stdout-001.log) y
  [generación activa de laboratorio](lab-manifest.json).

Los recibos conservan argumentos, tiempo y código de salida. Los casos de
prueba usan temporales del contenedor. La evidencia de la prueba histórica
identifica documentos y fragmentos sin reproducir el texto de los pasajes.

## Compatibilidad de la CLI con PowerShell

El modo heredado entregó `{consulta:PRO-SEG-015,top_k:3}` como argumento y la
CLI original terminó con código 2. En Windows PowerShell 5.1.26100.9711,
los [tres comandos con opciones](../../../docs/validacion-dev-hasta-f5.md#3-comprobar-el-estado-del-volumen-existente)
terminaron con código 0 en Docker `dev`.

| Operación | Estado observado | Revisión | Correlación |
| --- | --- | --- | --- |
| Baseline, búsqueda PRO-SEG-015 | `abstencion` | 1 | `6662a452-6964-4a90-abd4-cc125b73f682` |
| Laboratorio, búsqueda P-101 | `abstencion` | 13 | `71c5cd8c-a5c1-4519-9eee-b6786fe354df` |
| Laboratorio, obtención FIC-ACT-P101 | `denegado` | 13 | `6779f412-c60c-44e8-9297-665c06513c27` |
