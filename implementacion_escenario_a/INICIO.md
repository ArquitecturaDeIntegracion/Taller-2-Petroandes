# Prompt para iniciar un chat nuevo de Codex

Copia el siguiente texto en Codex después de abrir esta carpeta en VS Code:

```text
Lee AGENTS.md, knowledge/00-indice.md y docs/estado.md de esta carpeta.
Trabaja como arquitecto e implementador educativo de PetroAndes.
Usa $petroandes-desarrollo y reanuda la fase activa indicada en docs/estado.md.
Primero ejecuta validación e inventario con el intérprete local del README.
F0 tiene evidencia Windows y F1 está parcial; lee la fase necesaria del plan
mediante tools/read_source.py. Si cambió el entorno, revalida sus dependencias.
Docker Linux ya está comprobado. La siguiente fase técnica es F2, todavía sin implementar.
Valida las ediciones con el perfil dev de Docker siguiendo docs/docker-validacion.md.
Usa petroandes/paths.py, referencias relativas y .cache fuera de .venv.
Consulta el README para ejecución, depuración y reconstrucción de dependencias.
Continúa con las tareas autorizadas que no dependan de decisiones humanas
pendientes. No confundas el inventario del paquete con haber terminado F0.
Desarrolla solo la alternativa Python con Qdrant y composición extractiva.
Usa las habilidades de recuperación MCP y evaluación cuando correspondan.
Conserva los originales y los entregables anteriores del taller.
No inventes certificaciones, respuestas esperadas, hashes ni métricas.
Cada archivo de texto nuevo de esta carpeta debe tener como máximo 200 líneas.
Actualiza docs/estado.md con evidencias, bloqueos reales y próximo paso.
```
