# Evidencia técnica de F8

Corrida del 8 de noviembre de 2026 en Docker Desktop con el perfil `dev`.
El [resumen](summary.json) conserva el comando, el hash de la suite, el
checkpoint de laya y los resultados. Cada directorio `T01` a `T04` contiene
la entrada, respuesta, traza, transcripción de Inspector y evaluación.

Las cuatro llamadas coincidieron por Python y MCP, salvo el identificador
de correlación. Se verificaron dos afirmaciones con citas y texto literal.
Laya marcó 2 de 2 afirmaciones como respaldadas y 3 de 9 candidatos como
pertinentes. Las dos búsquedas respondidas recuperaron sus secciones
esperadas entre los primeros cinco resultados. Estos conteos corresponden
a controles técnicos sin calibración.

Docker registró agotamiento de memoria en una corrida anterior cuando
coincidieron los modelos de recuperación, evaluación y el Inspector anterior.
La corrida conservada separó la captura de los juicios en procesos sucesivos,
tras retirar el contenedor del puerto 6276. [Guía para reproducir](../../../docs/validacion-dev-f8.md).

## Regresión y estructura

```powershell
docker.exe compose --profile dev build dev
docker.exe compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider --basetemp /tmp/validacion-f8
docker.exe compose --profile dev run --rm -T dev tools/validate_agent.py
```

La construcción terminó con código 0. Pasaron 178 pruebas en 140,28 segundos.
El validador devolvió `OK` con 2841 archivos textuales y un máximo de 196 líneas.
