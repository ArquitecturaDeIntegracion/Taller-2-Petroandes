# Usar PetroAndes desde el Inspector web

## Iniciar y conectar

1. Abre Docker Desktop en modo contenedores Linux. En PowerShell, sitúate en
   `implementacion_escenario_a`, donde está `compose.yaml`.
2. Inicia el Inspector. La primera ejecución puede tardar mientras Docker
   construye la imagen del proyecto.

   ```powershell
   docker.exe compose --profile inspector up --build -d inspector-web
   ```

3. Espera a que se prepare la copia histórica y abre el
   [Inspector web local](http://127.0.0.1:6274/). En **Servers**, activa
   **petroandes** para los casos 1 y 2 o **petroandes-historico-f7** para los
   casos 3 y 4. Cuando muestre **Connected**, abre **Tools**.

Para cambiar de contexto, vuelve a **Servers**, desactiva la conexión actual
y activa la otra. Las cuatro llamadas se ejecutan en la misma dirección web.
El arranque requiere el modelo E5 en el volumen y las dos primeras llamadas
usan el catálogo habitual preparado en la [validación de F5](validacion-dev-hasta-f5.md).

La interfaz muestra **Read-only session** porque el catálogo viene del
proyecto. Puedes ejecutar las herramientas y ver sus resultados. El navegador
recibe automáticamente el token de la sesión al cargar la página local.
[Documentación del Inspector web](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/web).

## 1 Búsqueda sin evidencia en petroandes

1. En **Tools**, selecciona `buscar_documentos`.
2. En **Consulta**, escribe `Presión de descarga documentada de P-101.`.
   Pon `3` en **Top K** y deja los filtros vacíos.
3. Pulsa **Execute Tool** y revisa el resultado. En el volumen habitual del
   laboratorio, con la revisión 13, espera `estado` igual a `abstencion`,
   `sin_evidencia_autorizada` como motivo y listas de evidencia y afirmaciones vacías.
   La primera búsqueda puede tardar mientras se carga el modelo local.

## 2 Obtención denegada en petroandes

1. Selecciona `obtener_fragmento`.
2. Introduce `FIC-ACT-P101` en **Doc Id**, `2` en **Version Documental** y `2`
   en **Section Id**. La versión y la sección son cadenas de texto.
3. Pulsa **Execute Tool**. En el mismo contexto, espera `estado` igual a
   `denegado` y el motivo `evidencia_no_autorizada`, con partes y citas vacías.

**Protocol** muestra las solicitudes MCP y sus respuestas. Un `OK` en esa
pestaña indica que la llamada se completó. El resultado de la herramienta
indica si el contexto documental autoriza devolver evidencia.

## 3 y 4 Búsquedas autorizadas en petroandes historico f7

Selecciona `buscar_documentos`, configura los campos y pulsa **Execute Tool**
para cada caso. Ambos devuelven `respondida` en la copia histórica.

| Caso | Consulta | Campos | Resultado esperado |
| --- | --- | --- | --- |
| 3 | `Presión de descarga documentada de P-101.` | **Top K** `3`, **Tipo** `ficha`, **Activo** `P-101`, **Tramo** vacío | Diseño `1.180 psi` y alarma `1.240 psi`, con cita a `FIC-ACT-P101` v2, sección `2`. |
| 4 | `Localice el límite de incertidumbre de medición de RES-CREG-0043-2024.` | **Top K** `3`, **Tipo** `resolucion`, **Activo** y **Tramo** vacíos | `0,3 %` en puntos de transferencia de custodia, con cita a `RES-CREG-0043-2024`, artículo 2. |

Al pasar del caso 3 al 4, pulsa **Close results** y activa **Edit as JSON**.
Reemplaza todos los argumentos por este objeto y pulsa **Execute Tool**.
Así se elimina la clave `activo` que conserva el formulario al borrar su valor.

```json
{
  "consulta": "Localice el límite de incertidumbre de medición de RES-CREG-0043-2024.",
  "top_k": 3,
  "filtros": {"tipo": "resolucion"}
}
```

El contexto histórico reproduce la autorización académica registrada en la
revisión 13. En la exposición, repetir la pregunta de P-101 en ambos
contextos permite mostrar la diferencia de permisos con la misma herramienta.

## Comprobar y detener el servicio

Si la página no abre, comprueba que el servicio esté en ejecución y publique
el puerto local `127.0.0.1:6274`.

```powershell
docker.exe compose --profile inspector ps inspector-web
```

Si Docker indica que el puerto está ocupado, libera `6274` y vuelve a iniciar
el servicio. Tras reiniciarlo, recarga la página y activa de nuevo `petroandes`.
Puedes detenerlo al terminar con este comando.

```powershell
docker.exe compose --profile inspector stop inspector-web
```
