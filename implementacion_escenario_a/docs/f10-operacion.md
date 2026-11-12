# Operación local de F10

F10 utiliza un catálogo SQLite por perfil y una proyección por contexto de
servicio. Los comandos administrativos corren por turnos con el servidor que
usa el mismo almacenamiento local. El consumidor procesa el outbox bajo
demanda. El operador vuelve a ejecutar `propagar` después de una decisión, un
cambio de contenido o al vencer un permiso.

## Reconstruir desde los PDF en un espacio aislado

Desde PowerShell en la carpeta de implementación, prepara una ruta persistente
visible para los contenedores sucesivos. Los comandos usan el contexto
habitual, de modo que una carga base válida publica cero fragmentos consultables.

```powershell
$raiz = 'reports/portable/f10-operacion-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$artefactos = "$raiz/artefactos"
docker.exe compose --profile dev run --rm -T -e "PETROANDES_ARTIFACTS_DIR=$artefactos" dev -m petroandes.catalog init --profile laboratorio --evidence-dir "$raiz/f2"
docker.exe compose --profile dev run --rm -T -e "PETROANDES_ARTIFACTS_DIR=$artefactos" dev -m petroandes.extract --profile laboratorio --output-dir "$raiz/f3"
docker.exe compose --profile dev run --rm -T -e "PETROANDES_ARTIFACTS_DIR=$artefactos" dev tools/f10.py --output-dir "$raiz/consolidacion" consolidar --stage "$raiz/f3/manifest.json"
```

Espera revisión **1**, **19 documentos**, **cero decisiones de certificación**,
**cero fragmentos publicados** y **un evento confirmado**. El catálogo incluye
cuatro exclusiones y quince documentos pendientes. El informe conserva el
manifiesto del índice, sus huellas y los inventarios en JSONL.

```powershell
docker.exe compose --profile dev run --rm -T -e "PETROANDES_ARTIFACTS_DIR=$artefactos" dev tools/f10.py --output-dir "$raiz/replay" propagar --evento 1
```

Espera `evento_ya_confirmado` y cero eventos confirmados. El replay de un
evento ya confirmado funciona sin cargar el modelo ni el staging. Ejecutar
`propagar --stage <manifiesto-f3>` sin `--evento` reconcilia el estado vigente
aunque el outbox esté vacío, por ejemplo cuando vence un permiso.

## Registrar cambios revisados

- `registrar-pdf --revision N corpus/pdf/<familia>/<archivo>.pdf` registra
  los metadatos y la huella leídos del PDF. Si la huella cambia, el permiso
  anterior deja de aplicar. Prepara un staging F3 nuevo antes de publicar
  contenido modificado.
- `decision --revision N <archivo.json>` recibe un `DecisionRecord` como los
  exportados por [el laboratorio](../evidence/lab/20261103/registration/decisions/).
  Para una nueva decisión, incluye un ID nuevo y la revisión `N+1`.
  Usa `excluido` para revocar y una decisión explícita `certificado` con
  el ámbito, grupos, usos y fechas revisados para aprobar o cambiar permisos.
- `sustituir --revision N <archivo.json>` recibe `observacion`, `relacion`
  y `revisor_humano`. Registra antes ambos PDF. La observación excluye la
  huella anterior, y la relación cita el PDF del sucesor y apunta al anterior.
  El sucesor requiere su propia decisión para quedar consultable.

Después, ejecuta `propagar --stage <manifiesto-f3>`. Para cambios solo de
gobierno sirve el staging anterior si aún coincide con los PDF y cubre el
conjunto elegible. El consumidor verifica y activa el índice completo antes
de confirmar eventos. Si falla entre esos pasos, el próximo intento
revalida y reutiliza la generación preparada. Cada ejecución informa hasta
tres intentos. Tras agotarlos, corrige la causa y usa un directorio nuevo.

## Reindexar y recuperar

`reindexar --stage <manifiesto-f3> --operacion <id>` construye otra colección
y compara sus vectores para las entradas que conserva sin cambios. Usa un ID
nuevo para iniciar otra reconstrucción. `revertir <generation_id>` vuelve
a una generación registrada si conserva revisión, contexto y evidencia
elegible. Guarda el ID activo antes de reindexar.

En F10 se reconstruye el bundle y la partición fijados en el proyecto.
Probar una migración a otro bundle o partición requiere versionar sus
contratos y preparar su referencia. Los vectores de fingerprints distintos
se mantienen separados. Para restaurar derivados, cierra el cliente local
y copia juntos Qdrant, las proyecciones y sus manifiestos o reconstruye
desde los PDF. Conserva como autoridad el catálogo vigente.
