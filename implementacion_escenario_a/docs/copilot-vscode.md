# Exposición de PetroAndes desde Copilot en VS Code

Abre Docker Desktop en modo Linux y abre la carpeta `implementacion_escenario_a`
en VS Code. El proyecto usa la imagen y los volúmenes del perfil Docker `dev`.
La configuración del espacio de trabajo inicia los dos servidores por stdio.
[Configuración MCP de VS Code](https://code.visualstudio.com/docs/agents/reference/mcp-configuration).

En el chat de GitHub Copilot, crea una sesión con destino **Local**. Puedes
pegar una pregunta de esta guía o ejecutar su prompt guardado.

## Preguntas en lenguaje natural

Copia solo el texto de cada recuadro y envíalo como un mensaje de chat. Para
probar cada caso por separado, abre un chat nuevo. Expande la tarjeta de la
llamada MCP y comprueba el servidor, la herramienta y el resultado antes de
comparar la respuesta de Copilot con el esperado.

### 1. Búsqueda en el contexto habitual

```text
Usa buscar_documentos del servidor petroandes-local para buscar la presión de descarga documentada de la bomba P-101. Pide hasta tres resultados. Responde solo con lo que devuelva esa herramienta e indica el estado y el motivo si falta evidencia autorizada.
```

**Resultado esperado.** `abstencion` con motivo `sin_evidencia_autorizada`.

### 2. Obtención directa de la ficha en el contexto habitual

```text
Usa obtener_fragmento del servidor petroandes-local para pedir la sección 2 del documento FIC-ACT-P101, versión 2. Indica el estado que devuelve el MCP y el motivo si deniega el acceso.
```

**Resultado esperado.** `denegado` con error `evidencia_no_autorizada`.

### 3. Presión de descarga de P-101 en el laboratorio histórico

```text
Consulta la herramienta buscar_documentos del servidor petroandes-historico-f7. ¿Cuál es la presión de descarga de diseño de la bomba P-101 y cuál es su límite de alarma? Cita el documento, la versión, la sección y la página.
```

**Resultado esperado.** `respondida`, con **1.180 psi** de diseño y **1.240 psi**
como límite de alarma. Ficha `FIC-ACT-P101`, versión 2, sección 2 («Datos de
operación»), página 1.

### 4. Incertidumbre de medición en el laboratorio histórico

```text
Usa buscar_documentos del servidor petroandes-historico-f7 y filtra por tipo resolución. ¿Qué límite de incertidumbre combinada de medición fija RES-CREG-0043-2024 para los puntos de transferencia de custodia? Cita el artículo y la página usando el resultado del MCP.
```

**Resultado esperado.** `respondida`, con un límite de **0,3 %** en
`RES-CREG-0043-2024`, artículo 2, página 1.

La pregunta libre del caso 3 se ejecutó en Copilot y devolvió los dos valores
con su cita. Los esperados de los otros tres casos se tomaron de las pruebas
de los prompts guardados. [Evidencia de los cuatro prompts](../evidence/f7/20261108/copilot-vscode.md).

## Prompts guardados

Escribe `/petroandes-` en el chat y selecciona un prompt. También puedes abrir
la paleta con `Ctrl+Shift+P`, ejecutar **Chat: Run Prompt** y elegir el mismo
nombre. [Prompts reutilizables de VS Code](https://code.visualstudio.com/docs/agent-customization/prompt-files).

| Prompt | Servidor | Resultado esperado |
| --- | --- | --- |
| `/petroandes-01` | `petroandes-local` | `abstencion` por falta de evidencia autorizada. |
| `/petroandes-02` | `petroandes-local` | `denegado` al pedir la sección 2 de la ficha P-101. |
| `/petroandes-03` | `petroandes-historico-f7` | `respondida`, 1.180 psi de diseño y 1.240 psi de alarma en la ficha. |
| `/petroandes-04` | `petroandes-historico-f7` | `respondida`, límite de 0,3 % en el artículo 2 de la resolución. |

La primera consulta histórica prepara una copia temporal del catálogo y el
índice de F7. La primera llamada histórica por stdio tardó unos 72 segundos
en el equipo de prueba. Las siguientes reutilizan esa copia mientras el
servidor esté en ejecución. Para la exposición, puedes ejecutar el prompt
03 o 04 antes de mostrar el chat. Expande la llamada para comprobar el
nombre del servidor, los argumentos y el resultado original de MCP.

Si un servidor aparece detenido, usa **MCP: List Servers** en la paleta y
selecciona **Start Server**. El nombre `petroandes-local` identifica el
contexto habitual de la [guía del Inspector](inspector-web.md) dentro de VS Code.
Los dos clientes se pueden abrir por separado. El Inspector web es útil
para ver la transcripción del protocolo en el navegador.

El 11 de noviembre se encontró el servidor histórico en estado **Error**.
**Start Server** lo llevó a **Running**. Después se abrió un chat nuevo y
se ejecutó la consulta de incertidumbre con resultado `respondida`,
**0,3 %** y cita al artículo 2, página 1.
[Recibo de la prueba en VS Code](../evidence/f7/20261111-vscode/conexion.md).
