# Regresión en Docker dev

Comando ejecutado desde la raíz de la aplicación:

```text
docker compose --profile dev run --rm -T dev -m pytest -q -p no:cacheprovider
```

Salida observada y código de terminación registrados en la sesión técnica
del agente el 12 de noviembre de 2026, America/Bogota:

```text
........................................................................ [ 40%]
........................................................................ [ 80%]
....................................                                     [100%]
180 passed in 231.28s (0:03:51)
exit_code: 0
```

Este recibo transcribe el resultado de la herramienta de ejecución; no es
una captura independiente de stdout a archivo. Los ensayos específicos de
la conexión única sí conservan sus llamadas y salidas en `sdk/` e `inspector/`.
La evaluación formal de ajuste y reserva no se ejecutó.
