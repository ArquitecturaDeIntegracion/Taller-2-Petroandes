# Validación del Inspector web de F7

Fecha 2026-11-08, America/Bogota. Docker Desktop en Windows con contenedores
Linux. Inspector 2.13.0 en la imagen `petroandes-educativo:local`.

## Reproducción

```powershell
docker.exe compose --profile inspector config --quiet
docker.exe compose --profile inspector up --build -d inspector-web
docker.exe compose port inspector-web 6274
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:6274/
curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:6274/api/config
curl.exe -s -o NUL -w "%{http_code}" -H 'Origin: https://example.com' http://127.0.0.1:6274/api/config
curl.exe -s -o NUL -w "%{http_code}" -H 'Host: example.com' http://127.0.0.1:6274/
```

Los cambios se encuentran en `compose.yaml`, `config/inspector-web.json` y
la [guía web](../../../docs/inspector-web.md). Tras ajustar la red dedicada
se recreó el contenedor con `docker.exe compose --profile inspector up -d
inspector-web`. Docker informó `127.0.0.1:6274`. La página devolvió HTTP 200
y la consulta de la API sin credencial devolvió HTTP 401.
Los encabezados de origen y host externos devolvieron HTTP 403.

## Observación en el navegador

En **Servers**, `petroandes` pasó a **Connected**, con transporte **STDIO**
y versión MCP `2025-11-25`. **Tools** enumeró dos herramientas.

| Herramienta | Entrada | Resultado observado |
| --- | --- | --- |
| `buscar_documentos` | `consulta` = `Presión de descarga documentada de P-101.`, `top_k` = `3` | `estado` = `abstencion`, `motivo_abstencion` = `sin_evidencia_autorizada`, `revision_gobierno` = `13` |
| `obtener_fragmento` | `doc_id` = `FIC-ACT-P101`, `version_documental` = `"2"`, `section_id` = `"2"` | `estado` = `denegado`, `error` = `evidencia_no_autorizada`, `revision_gobierno` = `13` |

## Regresión Docker dev

```powershell
docker.exe compose --profile dev run --rm -T dev tools/validate_agent.py
docker.exe compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider --basetemp /tmp/validacion-inspector-web
```

El validador terminó con `OK` y la suite aprobó 178 pruebas en 137,09 segundos.
