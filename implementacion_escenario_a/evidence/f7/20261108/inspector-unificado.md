# Pruebas web de exposición en un puerto

Fecha 2026-11-08, America/Bogota. Docker Desktop en Windows, Inspector 2.13.0.

```powershell
docker.exe compose --profile dev build dev
docker.exe compose --profile inspector up -d inspector-web
```

En `http://127.0.0.1:6274/`, **Servers** mostró `petroandes` y
`petroandes-historico-f7`. Se desconectó la primera antes de activar la
segunda. Las cuatro pruebas siguieron la [guía web](../../../docs/inspector-web.md).

| Caso | Conexión | Resultado observado |
| --- | --- | --- |
| 1 | `petroandes` | `abstencion` con `sin_evidencia_autorizada`. |
| 2 | `petroandes` | `denegado` con `evidencia_no_autorizada`. |
| 3 | `petroandes-historico-f7` | `respondida`, `FIC-ACT-P101` v2 sección 2, diseño `1.180 psi` y alarma `1.240 psi`. |
| 4 | `petroandes-historico-f7` | `respondida`, `RES-CREG-0043-2024` artículo 2, límite `0,3 %`. |

El formulario conservó `activo` como cadena vacía al borrar `P-101` tras el
caso 3. Se observó `parametros_invalidos`. Se sustituyeron los argumentos
con **Edit as JSON**, omitiendo esa clave, y la llamada devolvió el resultado
del caso 4. Se detuvo el contenedor anterior publicado en 6276.
