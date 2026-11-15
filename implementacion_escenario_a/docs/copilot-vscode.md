# PetroAndes desde Copilot con una conexión

Abre `implementacion_escenario_a` como carpeta en VS Code y mantén Docker
Desktop activo en modo Linux. `.vscode/mcp.json` declara únicamente
`petroandes`, que ejecuta Docker `dev` y `python -m petroandes.demo` por stdio.
La [guía web](inspector-web.md) usa exactamente la misma configuración de
demostración, revisión 15 y reloj histórico del 8 de noviembre de 2026.

## Iniciar y comprobar

Tras actualizar a F9.2, reconstruye la imagen y reinicia `petroandes` desde
**MCP: List Servers**. Cada llamada deja un recibo por `correlation_id` en
`reports/portable/mcp-audit/`. La [guía F9.2](validacion-dev-f9-2.md) muestra
cómo consultarlo y cómo usar el cliente aislado. Copilot conserva sus propias
capacidades; no queda aislado por el sandbox del arnés.

1. Construye la imagen y prepara E5 siguiendo la [guía web](inspector-web.md).
2. Pulsa `Ctrl+Shift+P`, ejecuta **MCP: List Servers** y elige **petroandes**.
   Pulsa **Start Server** si está detenido y espera **Running**.
3. Abre un chat nuevo de GitHub Copilot con destino **Local**, modo **Agent**
   o equivalente y herramientas habilitadas. Deben aparecer
   `buscar_documentos` y `obtener_fragmento` de `petroandes`.
4. Envía un prompt. La primera llamada prepara los índices; puede tardar
   varios minutos. Expande su tarjeta para verificar argumentos y resultado.

Si VS Code conserva herramientas de los nombres anteriores, recarga la ventana
con **Developer: Reload Window** y abre un chat nuevo. El proyecto elimina las
entradas anteriores de `.vscode/mcp.json` y deja `.mcp.json` sin duplicados.
No necesitas iniciar Inspector para usar Copilot.

## Cuatro prompts en lenguaje natural

### 1 Buscar la presión documentada

```text
Usa buscar_documentos del servidor petroandes. Busca la presión de descarga documentada de P-101, con top_k 3 y filtros tipo ficha y activo P-101. Conserva las condiciones y cita documento, versión, sección y página.
```

Esperado: `respondida`, **1.180 psi** de diseño y **1.240 psi** de alarma,
`FIC-ACT-P101`, versión 2, sección 2, página 1.

### 2 Leer una sección autorizada

```text
Usa obtener_fragmento del servidor petroandes con doc_id FIC-ACT-P101, version_documental "2" y section_id "2". Muestra el estado, las partes y sus citas.
```

Esperado: `encontrado`, los mismos valores de la ficha y su cita.

### 3 Comprobar una denegación

```text
Usa obtener_fragmento del servidor petroandes con doc_id PRO-MED-007, version_documental "1" y section_id "3". Indica el estado y el error devueltos; usa únicamente el resultado de esa llamada.
```

Esperado: `denegado`, `evidencia_no_autorizada`, partes y citas vacías.

### 4 Buscar la incertidumbre

```text
Usa buscar_documentos del servidor petroandes. Localiza el límite de incertidumbre de medición de RES-CREG-0043-2024, con top_k 3 y filtro tipo resolucion. Cita el artículo y la página usando el resultado MCP.
```

Esperado: `respondida`, incertidumbre combinada máxima **0,3 %**, artículo 2,
página 1. El código de sección devuelto es `articulo-2`.

## Prompts guardados y controles adicionales

Escribe `/petroandes-` o usa **Chat: Run Prompt** para elegir:

| Prompt | Herramienta | Resultado |
| --- | --- | --- |
| `/petroandes-01` | buscar_documentos | P-101 respondida |
| `/petroandes-02` | obtener_fragmento | Ficha encontrada |
| `/petroandes-03` | obtener_fragmento | Versión excluida denegada |
| `/petroandes-04` | buscar_documentos | Incertidumbre respondida |

Todos usan `petroandes`. Los argumentos exactos están en cada archivo
`.github/prompts/petroandes-0N.prompt.md`. El resultado original MCP es la
referencia al comparar con la redacción del modelo.

El [Inspector](inspector-web.md) documenta los parámetros de firmware y del
anexo malicioso. Puedes pedir las mismas llamadas desde Copilot. El firmware
debe devolver 7.4 y sus condiciones; el anexo debe dar `abstencion` con
`evidencia_insuficiente`. El MCP trata ese texto como dato no confiable.
Los ensayos especiales de auditoría y cambio de permisos siguen en F9/F10,
con copias aisladas; no se añade otra conexión de presentación.

Consulta el [ADR](adr-0013-mcp-demostracion-unica.md) y la
[evidencia de la validación](../evidence/f7/20261112-demo-unica/README.md).
