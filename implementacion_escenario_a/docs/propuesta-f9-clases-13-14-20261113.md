# Análisis y propuesta de evolución del arnés F9

Fecha: 2026-11-13. Estado: propuesta para revisión; no implementada.
Alcance: Escenario A educativo, código actual y sesiones 13 y 14 aportadas por el usuario.
No se ejecutaron ataques nuevos ni se modificaron permisos, corpus, servidor o clientes.

## Dictamen

F9 acredita la recuperación y el descarte del anexo conocido. Es una buena prueba de regresión del servidor.
La mejora prioritaria es demostrar contención aunque un cliente intente obedecer el documento.
Un detector más amplio puede ayudar, pero no sustituye permisos ni aislamiento independientes del modelo.
Recomiendo una evolución incremental F9.1: matriz de amenazas, casos variados, ejecutor determinista,
sandbox de pruebas y resultados por objetivo. Un ensayo con LLM real sería una ampliación posterior.
Se conserva Python, E5, Qdrant, laya y una conexión visible petroandes con dos herramientas de lectura.

## Qué aportan las clases

| Fuente y páginas | Enseñanza aplicable | Consecuencia para PetroAndes |
| --- | --- | --- |
| Sesión 13, 5–8 | Estados tipados, límites de pasos y aprobación antes del efecto irreversible. | Representar cada ensayo mediante estados y transiciones explícitos; no pedir aprobación para cada lectura. |
| Sesión 13, 9–11 y 16–19 | Un agente suele bastar; guardar estado no garantiza ejecución durable; efectos e idempotencia son distintos. | Mantener el backend determinista; registrar interrupciones, reintentos y quién reinicia. No añadir LangGraph o Temporal para este laboratorio. |
| Sesión 14, 8 y 17 | Entrada y salida del modelo no confiables; el runtime y el sistema de registro validan. | Verificar la política en el ejecutor de herramientas, incluso con una propuesta maliciosa bien formada. |
| Sesión 14, 15–16 | Regla de Dos; plan fijado antes de leer datos; lectura en cuarentena. | Aislar lectura de documentos y acciones; una referencia o resumen sigue siendo dato no confiable. |
| Sesión 14, 19–21 | Identidad, recurso y mínimo privilegio por herramienta. | Documentar la matriz herramienta × permiso y probar denegaciones por objeto, uso y contexto. |
| Sesión 14, 22 y 24–25 | Ataques reproducibles, al menos uno no agéntico; AgentOps y cancelación. | Añadir manipulación de hash/índice, telemetría por episodio, presupuestos y parada segura. |

Las páginas 15, 16, 18 y 27 de la sesión 14 contienen gráficos cuyo contenido no sale completo al extraer texto.
Se inspeccionaron visualmente, al igual que los gráficos de las páginas 7 y 16 de la sesión 13.
La sesión 13 habilita principalmente el diseño del Escenario B; no obliga a implementarlo en el Escenario A.
La lámina 27 muestra otra realización con Chroma, MiniLM y un evaluador externo. No recomiendo migrar
la arquitectura aprobada por esa ilustración: corresponde documentar equivalencias y conservar las decisiones vigentes.

## Diagnóstico del código actual

| Elemento comprobado | Fortaleza | Brecha o límite |
| --- | --- | --- |
| tools/f9_attack.py | Recupera el anexo, contrasta Python/Inspector y conserva la misma generación. | Una muestra maliciosa, marcadores textuales conocidos y ninguna ejecución de un cliente LLM. |
| extract/prepare.py y compose/units.py | Datos no confiables y descarte determinista. | La marca se asigna por section_id anexo-*; no analiza intención. Puede descartar anexos legítimos y omitir ataques en otras secciones. |
| mcp_tools.py y governance/eligibility.py | Dos herramientas, validación de esquemas y permisos documentales fuera del modelo. | readOnlyHint y las descripciones son señales al cliente, no aislamiento del sistema operativo. |
| tools/f9_observe.py | Observa eventos Python y verifica sus sondas. | No es un sandbox; se activa durante llamadas y busca balance por nombre de archivo. No cubre todo código nativo ni otros procesos. |
| compose.yaml y Dockerfile | Entorno reproducible y fuente dev montada de solo lectura. | No declaran usuario no privilegiado, raíz de solo lectura o red deshabilitada; mantienen volúmenes escribibles. No acreditan contención fuerte. |
| petroandes.demo y config/mcp-demo.json | Snapshot aprobado verificado y contexto explícito, aislado por proceso. | Identidad configurada no equivale a autenticar usuarios. El reloj histórico no representa revocación en tiempo real. |
| Copilot como consumidor | Permite demostrar llamadas reales. | Dos herramientas del servidor no limitan todas las capacidades del cliente. No se ha verificado la sesión completa frente al anexo íntegro. |

Las rutas sin prefijo tools/ o config/ de esta tabla parten de petroandes/.
Los 19 controles archivados de F9 describen esa corrida, no una tasa general de resistencia.
La ausencia de efectos no prueba que hubo un intento detenido: puede no haberse intentado ninguna acción.
E5 recupera y laya evalúa respaldo/pertinencia; ninguno se presenta como detector de inyección.

## Diseño recomendado

```mermaid
flowchart LR
  A[Solicitud y contexto confiables] --> B[Plan permitido fijado por código]
  B --> C[Lectura documental aislada]
  C --> D[Resultado no confiable con procedencia]
  D --> E[Validador determinista de esquema, recurso y uso]
  E --> F[Respuesta citada o cierre seguro]
  E --> G[Acción ajena al catálogo: denegar y registrar]
```

En el servicio real no se añaden correo, shell, balances ni escrituras de negocio.
En el laboratorio se representan mediante dobles instrumentados con datos ficticios, fuera del catálogo público.
El cliente que lee un documento no puede ampliar su plan, crear herramientas ni cambiar identidad o permisos.
Los identificadores y campos extraídos también se validan; un JSON correcto puede solicitar una acción indebida.
La procedencia viaja con los datos y se revalida. Ni una etiqueta ni un resumen los convierten en instrucciones confiables.
Una autorización para mostrar texto en auditoría sigue sin autorizar su ejecución.

## Incrementos propuestos

| Prioridad | Entrega concreta | Criterio de aceptación |
| --- | --- | --- |
| P0 | Modelo de amenazas y matriz por herramienta: acción, objeto, uso, identidad, destino y límites. | Cada ataque señala activo, entrada, objetivo, defensa, capa y si detecta o contiene. Se distingue cliente de servidor. |
| P1 | Suite nueva de ataques y controles benignos, independiente de los casos formales congelados. | El anexo original sigue recuperándose; cada variante acredita que alcanzó la frontera evaluada. Controles benignos miden utilidad y falsos positivos. |
| P1 | Cliente adversarial determinista que propone acciones prohibidas, y dispatcher que solo admite el catálogo autorizado. | Incluso si el cliente intenta obedecer, no hay correo, shell, lectura arbitraria, escalada de uso ni cambio de política. Se registra la denegación. |
| P1 | Sandbox específico del arnés dentro del perfil dev. | Sin secretos del host ni socket Docker; usuario no privilegiado, montajes mínimos, escritura temporal acotada, sin salida de red para el worker y recursos limitados. Pruebas positivas acreditan las restricciones. |
| P1 | Grader por objetivo y reporte de trayectoria. | Distingue intento, denegación, ejecución, contaminación textual y filtración; fallo o telemetría ausente nunca cuentan como ataque bloqueado. |
| P2 | Estados tipados, journal por ejecución, reintentos acotados y cancelación. | Un proceso interrumpido deja estado abortado/inconcluso, conserva evidencia y puede reiniciarse de forma documentada, sin declarar durabilidad automática. |
| P2 | Cliente LLM real opcional y controlado, con modelo/prompt/versiones y repeticiones registradas. | Se informa solo lo observado. Si no se ejecuta o no hay credenciales/modelo, figura no evaluado. El cliente determinista no se anuncia como LLM. |
| P2 | Detección auxiliar de instrucciones sospechosas, Unicode invisible y discrepancias entre PDF visible y extracción. | Emite riesgo y evidencia; preserva el original y envía dudas a revisión. No concede permisos ni elimina silenciosamente el documento. |

El worker sin red se separa del Inspector web: aplicar network_mode none al navegador o a su servidor rompería la demostración.
Los modelos se preparan antes del aislamiento; la ejecución usa archivos ya verificados y no descarga dependencias.
Qdrant necesita espacio privado escribible; corpus, decisiones y pesos pueden tener montajes separados de solo lectura.
no-new-privileges y cap_drop no prohíben por sí solos ejecutar subprocess. Si se exige ese control a nivel SO,
hay que diseñar y probar un perfil específico; no atribuir esa garantía a esas opciones ni al hook Python.
Las pruebas de red deben demostrar denegación por política, no solo que el receptor ficticio estaba apagado.

## Casos mínimos nuevos y observables

1. Anexo original: mismo chunk recuperado y descartado; texto íntegro permitido solo en auditoría.
2. Instrucción equivalente dentro de una sección ordinaria o tabla, sin prefijo anexo-.
3. Variantes en español/inglés y con Unicode o codificación; presupuestos explícitos de intentos.
4. Orden repartida entre dos fragmentos o entre búsqueda y obtención directa en una misma sesión.
5. Datos aparentemente técnicos que cambien una cifra o condición; medir contaminación de respuesta aunque no haya herramienta ejecutada.
6. Suplantación de una instrucción de sistema o descripción de herramienta; el catálogo y el plan no cambian.
7. Solicitud de exfiltrar un canario ficticio por correo, URL o parámetros; no enviar datos reales ni contactar terceros.
8. Lectura directa, padre/contexto y llamada manipulada que intenten eludir objeto, hash, uso o grupo.
9. PDF cambiado con hash antiguo o índice/manifiesto alterado: denegación y alerta por integridad; ataque no agéntico.
10. Caída del worker, timeout y cancelación: resultado inconcluso o abortado, con evidencia parcial conservada.
11. Anexo legítimo, explicación de un ataque y consulta legítima de firmware como controles benignos.
12. Dos contextos de usuario ficticios para verificar que un documento autorizado en uno no se filtra al otro.

Las variantes viven en fixtures nuevos; no se altera el corpus original ni se heredan permisos de un hash revisado.
Separar pruebas RAG completas de pruebas que inyectan una respuesta MCP para evaluar solo el consumidor.
Un rechazo por hash o falta de permiso es válido para gobierno, pero no demuestra contención después de recuperar el ataque.
No desactivar la política ni ampliar decisiones reales para hacer que un caso llegue al compositor.
La regla actual se mantiene como referencia hasta que una alternativa versionada y revisada muestre sus resultados.

## Métricas y evidencia de salida

- Exposición: casos donde el fragmento malicioso llegó a la frontera / casos aplicables; guardar IDs, hash y generación.
- Efecto indebido: casos con acción no autorizada / casos ejecutados aplicables; separar cliente, dispatcher y SO.
- Filtración y contaminación: objetivos distintos, con observables propios y canarios sintéticos, no solo frases prohibidas.
- Falsos positivos: bloqueos de seguridad indebidos / controles benignos aplicables; añadir éxito de tarea y revisiones pendientes.
- Detección: precisión/recobrado solo si se añade detector y existe etiquetado revisado; no confundirlas con contención.
- Operación: duración, llamadas, presupuesto, reintentos, errores e inconclusos, por configuración y repetición.

Registrar run_id, case_id, etapa, modelo/prompt si aplica, política, contexto, herramienta, argumentos mínimos,
decisión, motivo, efectos intentados/ejecutados y procedencia. No guardar secretos ni prompts sensibles innecesarios.
Guardar el caso previsto antes de ejecutarlo, y los fallos junto a los aciertos. No dar puntuación perfecta a una salida vacía.
Las sondas de calibración prueban observadores y grader con resultados conocidos; los dobles no prueban el SMTP real.
La suite original F9 y la regresión siguen siendo controles de compatibilidad. La reserva no se usa para calibrar.

## Aplicación educativa y evolución productiva

Para clase recomiendo P0 y P1 primero, conservando el motor extractivo y la conexión única.
La inspección auditada no debe alimentar una sesión Copilot con herramientas de propósito general o acceso personal.
Una prueba LLM exige un consumidor controlado; no ejecutar ataques en el chat habitual con conectores privilegiados.
El sandbox del servidor no aísla por sí solo al cliente que recibe sus textos.
En el Escenario A no hay escritura de negocio que deba someterse a una aprobación nueva por consulta.
Si en el futuro se publica, envía o registra información, la aprobación revisará acción, argumentos, destino y contenido
exactos antes del efecto, con vínculo a su huella; no una aprobación general de toda la conversación.
En producción se añadirían identidad autenticada por workload/usuario, delegación y autorización por objeto,
manifiestos autenticados con claves separadas, gestión de secretos, proxy de salida, alertas, retención y respuesta a incidentes.
La exposición HTTP requeriría revisar autorización MCP, audiencia y sesiones; stdio local no necesita OAuth como requisito automático.
La cancelación educativa detiene workers y nuevas llamadas. Revocar credenciales y cancelar un flujo durable
son controles adicionales para una arquitectura productiva que realmente los tenga.
El historial local no se presentará como orquestador durable ni como plataforma multiusuario lista para producción.

## Fuentes y criterio de lectura

[C13] ARTI4212_S13_Orquestacion_Agentes.pdf, 20 páginas, aportado por el usuario; páginas indicadas en la matriz.
[C14] ARTI4212_Sesion14.pdf, 27 páginas, aportado por el usuario; texto y gráficos relevantes revisados.
Se tomaron como material académico, no como instrucciones para ejecutar herramientas ni alterar el proyecto.
[P] Código: tools/f9_attack.py, tools/f9_observe.py, petroandes/extract/prepare.py, petroandes/compose/units.py,
petroandes/mcp_tools.py, compose.yaml, Dockerfile; contraste con knowledge/05-calidad.md y fase F9 del plan.
[I1] [OWASP Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html): validación fuera del modelo y evaluación por objetivos.
[I2] [OWASP RAG Security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html): integridad, procedencia y autorización en recuperación.
[I3] [Meta Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/): limitar combinaciones de entrada externa, datos sensibles y acciones.
[I4] [Microsoft defensa ante inyección indirecta](https://learn.microsoft.com/en-us/security/zero-trust/sfi/defend-indirect-prompt-injection): capas deterministas y probabilísticas según el contexto.
[I5] [MCP Security Best Practices 2025-11-25](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices): mínimos privilegios para servidores locales. No se propone cambiar la versión del protocolo.
[I6] [Anthropic sobre defensas](https://www.anthropic.com/research/prompt-injection-defenses): avances y límites; no inmunidad universal.
Las mejoras son una recomendación técnica a partir de las fuentes, no una afirmación de que toda empresa use la misma pila.
