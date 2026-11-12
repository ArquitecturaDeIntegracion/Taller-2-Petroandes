FROM python:3.12-slim-bookworm AS inspector-lock
COPY implementacion_escenario_a/config/inspector-npm-lock.zip /tmp/inspector-npm-lock.zip
RUN python -m zipfile -e /tmp/inspector-npm-lock.zip /lock

FROM node:22-bookworm-slim AS inspector
WORKDIR /opt/inspector
COPY --from=inspector-lock /lock/package.json /lock/package-lock.json ./
RUN npm ci --no-audit --no-fund

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8
ENV PETROANDES_INSPECTOR_DIR=/opt/inspector
WORKDIR /workspace/implementacion_escenario_a
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libstdc++6 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=inspector /usr/local/bin/node /usr/local/bin/node
COPY --from=inspector /opt/inspector /opt/inspector
COPY implementacion_escenario_a/requirements-portable.lock implementacion_escenario_a/requirements-dev.lock ./
# CPU: no se requiere GPU y no se arrastran bibliotecas CUDA al laboratorio.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 \
    && pip install --no-cache-dir -r requirements-dev.lock && pip check
COPY corpus/ /workspace/corpus/
COPY output/doc/ /workspace/output/doc/
COPY ["Contenido de la Actividad.docx", "ARTI4212_Caso_PetroAndes.pdf", "ARTI4212_Caso_PetroAndes.md", "contexto_arquitectura_integracion.md", "plan_trabajo_alternativa_1_escenario_a.md", "/workspace/"]
COPY implementacion_escenario_a/ ./
RUN pip install --no-deps --no-build-isolation -e .
ENTRYPOINT ["python"]
CMD ["tools/preflight.py"]
