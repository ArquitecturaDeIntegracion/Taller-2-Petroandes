# Verificación del ZIP de entrega

La huella del ZIP es
`264a05a74a7c5537840d8da090a270916b97d01394fb2706083e5f7b9ffbb4e7`.
Se reabrieron y cotejaron 1971 entradas, incluido el manifiesto.
La copia extraída pasó la verificación de estructura y referencias.
[Recibo del empaquetado](summary.json).

Desde esa copia se construyó la imagen `petroandes-entrega:f11-final`,
índice OCI `sha256:aa9a97bbf248a762cff35d7683565006d8ba456f4651a769f31fc47cb00fbec6`.
Se usó un proyecto Docker separado, artefactos temporales y el volumen
de modelos previamente descargados para F11. La ejecución arrancó en
`/tmp`, con el perfil `dev`. Los argumentos de Compose apuntaron al
`compose.yaml` de la extracción y a un override de prueba para la etiqueta
de imagen y el volumen externo de modelos.

```powershell
docker.exe @composeArgs build dev
docker.exe @composeArgs run --rm -T -w /tmp dev /workspace/implementacion_escenario_a/tools/preflight.py
docker.exe @composeArgs run --rm -T -w /tmp dev /workspace/implementacion_escenario_a/tools/f11_verify_delivery.py --output-dir reports/portable/verificacion-entrega
```

El inventario encontró los 19 PDF. El baseline extrajo 92 fragmentos,
publicó cero, se abstuvo y denegó la obtención de la versión excluida.
Inspector 2.13.0 listó las dos herramientas y devolvió la respuesta
histórica de P-101 en revisión 13, con paridad Python/MCP.
[Resultado de Docker](verificacion-docker/summary.json).

La comprobación es técnica. Los casos de evaluación formal conservan el
estado de revisión académica pendiente.
