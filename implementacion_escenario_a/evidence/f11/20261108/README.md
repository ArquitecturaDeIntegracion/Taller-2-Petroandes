# Reproducción de la entrega técnica F11

Fecha 2026-11-08, America/Bogota. Motor Docker Desktop Linux 28.3.2.
La preparación descargó E5 y laya en un volumen nuevo, separado del
laboratorio de uso habitual.

```powershell
$proyecto = 'petroandes-f11-20261108'
docker.exe compose -p $proyecto --profile dev build dev
docker.exe compose -p $proyecto --profile dev run --rm -T dev tools/f0.py e5 --output reports/portable/f11-modelos-20261108/e5.json
docker.exe compose -p $proyecto --profile dev run --rm -T dev tools/f0.py laya --output reports/portable/f11-modelos-20261108/laya.json
docker.exe compose -p $proyecto --profile dev run --rm -T -w /tmp dev /workspace/implementacion_escenario_a/tools/f11_check.py --output-dir reports/portable/f11-final-dev-20261108-195433
```

[Sonda de descarga E5](modelos-descarga/e5.json) ·
[Sonda de descarga laya](modelos-descarga/laya.json) ·
[Guía de reproducción](../../../docs/validacion-dev-f11.md).

La corrida integral terminó con código 0 y `status: passed`. Duró unos
22 minutos en este equipo, sin incluir la descarga. Empezó en `/tmp` con
artefactos ausentes y verificó las huellas de 45 fuentes originales al final.

| Control | Resultado observado |
| --- | --- |
| Reconstrucción | 19 PDF, 92 fragmentos extraídos y 0 publicados en baseline. La consulta se abstuvo y el acceso a PRO-MED-007 v1 se denegó. [Informe](corrida/baseline/reconstruccion.json). |
| Regresión | 180 pruebas aprobadas. [Salida](corrida/comandos/regresion/stdout-001.log). |
| Inspector | Dos herramientas verificadas y 58 puntos reabiertos. [F7](corrida/f7/summary.json). |
| laya | 2 de 2 afirmaciones respaldadas, 3 de 9 candidatos pertinentes y desviación en 0 de 4 casos diagnósticos. [F8](corrida/f8/summary.json). |
| Ataque y cambios | Descarte del anexo, paridad de auditoría y revisión 17 con 0 eventos pendientes. [F9](corrida/f9/summary.json) · [F10](corrida/f10/summary.json). |
| Entrega | 1698 archivos en el manifiesto, con rutas relativas y SHA-256. [Inventario](corrida/entrega/summary.json). |

[Resumen integral y recibos por etapa](corrida/summary.json).

La corrida técnica se distingue de la evaluación académica. Los cuatro
casos diagnósticos de F8 se conservan separados de los casos de ajuste y
reserva propuestos. Se registraron ocho propuestas de ajuste y dieciséis
de reserva pendientes de revisión. [Inventario académico](corrida/entrega/casos-academicos-001.jsonl).

## Imágenes y lock de Inspector

La corrida integral usó la imagen con índice OCI
`sha256:e41e204ef20553a5e57175637ff979aeebd45d69e878a095ea003efb64f383aa`.
Después se reconstruyó con `npm ci`, usando el mismo lockfile, bajo
`sha256:6776db09026d891b168c2a415a40c00c563def1ebfca8d30e6840b07715743b4`.
La reinstalación de Python pasó `pip check`. El inventario de sus 77
distribuciones y la huella del lockfile npm coincidieron en ambas imágenes.

La comparación estricta de npm detectó 120 paquetes en la primera imagen
y 123 en la segunda. Los tres adicionales son variantes opcionales para
musl de keyring, rolldown y lightningcss. Las dos imágenes usan Debian
con glibc. Se conserva la diferencia observada, junto con el inventario
de licencias de la imagen reconstruida.
[Comparación](comparacion-imagenes/summary.json) ·
[Diferencias npm](comparacion-imagenes/diferencias-npm.json).

En la imagen reconstruida, Inspector 2.13.0 listó y llamó a un servidor
mínimo por stdio. Con el servidor del proyecto, listó `buscar_documentos`
y `obtener_fragmento` y rechazó `top_k: 0` con `parametros_invalidos`.
[Sonda stdio](npm-ci-sonda/summary.json) ·
[Herramientas del proyecto y licencias](npm-ci-herramientas/summary.json) ·
[Recibo](npm-ci-comando/command.json).
