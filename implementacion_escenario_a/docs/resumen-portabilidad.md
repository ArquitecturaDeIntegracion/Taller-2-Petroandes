# Resumen ejecutivo: portabilidad del proyecto PetroAndes

Fecha: 2026-11-01. Alcance: preparar la continuación del desarrollo educativo.

El proyecto resuelve ahora sus ubicaciones a partir de la carpeta de aplicación,
admite configuración local y evita depender de la cuenta o del directorio de
trabajo original. Se añadieron instalación editable, depuración y una definición
Docker. Se comprobaron tanto la ejecución local como la imagen Linux y el perfil
`dev` con código montado del host. F2 está lista para iniciar su desarrollo técnico.

## Cambios implementados

| Área | Resultado |
| --- | --- |
| Rutas | Módulo central, overrides `PETROANDES_*`, referencias relativas y rechazo de escapes |
| Herramientas | Lectura, inventario, sondas y cierre F0 usan las raíces actuales |
| Evidencia | Informes nuevos con esquema 2 y marcadores de raíces; evidencia previa intacta |
| Modelos | Caché separada de `.venv`; migración de 14 archivos con hashes iguales |
| Dependencias | Lock portable con pywin32 condicionado a Windows; lock de desarrollo con debugpy |
| Paquete | pyproject e instalación editable, sin depender de cwd para importar el código |
| VS Code | Perfiles de inventario, pytest y conexión al debugger Docker |
| Docker | Imagen Python/CPU/Node/Inspector, Compose y volúmenes para caché/artefactos |
| Repositorio | Exclusiones para entornos, cachés, temporales, secretos locales e informes de ejecución |
| Continuidad | AGENTS, README, ADR y estado actualizados para trabajo portable |

## Evidencia de validación

- 36 pruebas aprobadas: 25 de contratos existentes y 11 nuevas de portabilidad.
- Copia aislada con espacios/acentos: inventario, validador y 36 pruebas aprobadas
  desde un cwd externo. Se reutilizó el intérprete; no es una instalación limpia.
- Instalación editable y dependencias locales comprobadas.
- E5 y laya ejecutados realmente offline desde la nueva ubicación de modelos.
- Inspector MCP ejecutó listado y llamada mínima con el servidor F0 real.
- debugpy verificó y alcanzó un breakpoint real; el proceso continuó con salida 0.
- Cierre F0 revalidado: 15 comprobaciones y hashes históricos conservados.
- Docker Linux construido: 19 comprobaciones aprobadas, incluidas 36 pruebas en
  imagen y 36 en `dev`, almacenamiento, corpus, MCP, breakpoint y modelos offline.

Los informes nuevos se generan localmente bajo `reports/portable/` y se excluyen
del repositorio: `debug.json`, `e5-offline.json`, `laya-offline.json`,
`closure-windows.json`, `mcp-host/summary.json`, `relocation-final.json` y `docker-build.json`.
Los nombres concretos pueden variar en próximas corridas; conserva destinos nuevos.
Las evidencias F0/F1 anteriores siguen en `evidence/`, sin reescribir rutas observadas.

## Límite pendiente y continuidad

El bloqueo anterior de Docker Desktop está resuelto. La evidencia nueva está en
`reports/portable/docker-validacion-20261101/checks-final/`; consulta el
[informe Docker y flujo F2](docker-validacion.md). Se corrigieron exclusiones de
contexto, salida UTF-8 y cierre DAP en Linux; Windows también conserva el breakpoint.
La compatibilidad comprobada corresponde a Linux x86-64 en esta máquina.

La entrega no cambia la vigencia documental ni acredita revisiones académicas:
se conservan cuatro excluidos y quince pendientes. F1 sigue parcial; F2 puede
continuar con catálogo y gobierno. El servicio final y la evaluación académica
siguen dentro del plan de desarrollo.

Consulta las instrucciones reproducibles en el [README](../README.md), la
[decisión técnica](adr-0006-portabilidad.md) y el [estado de reanudación](estado.md).
