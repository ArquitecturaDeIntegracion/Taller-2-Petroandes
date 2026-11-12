# ADR-0011 · Inspector web local para F7

Fecha 2026-11-08. Estado adoptado.

El Inspector CLI valida los contratos MCP de F7 con ensayos reproducibles.
El perfil de Compose `inspector` añade la interfaz de navegador para ejecutar
las mismas herramientas de forma manual y observar el intercambio MCP.

El servicio `inspector-web` reutiliza la imagen del proyecto con Inspector
2.13.0, los montajes de código de `dev` y los volúmenes de modelos y artefactos.
Carga un catálogo de solo lectura con `petroandes` y
`petroandes-historico-f7` por stdio. La primera conexión usa el volumen
habitual de `laboratorio`. La segunda reutiliza el contexto y la copia
temporal de la validación F7, con un índice separado y reloj de ensayo.
El protocolo `legacy` del Inspector negocia MCP `2025-11-25` con el SDK Python.

Docker publica la interfaz y la API en `127.0.0.1:6274` mediante una red
dedicada. El Inspector conserva el token generado por arranque, limita los
orígenes al puerto local y mantiene en memoria su almacén de secretos.
La ejecución manual se describe en la [guía del Inspector web](inspector-web.md).
