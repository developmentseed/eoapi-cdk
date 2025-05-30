ARG PYTHON_VERSION=3.11
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

ENV UV_CACHE_DIR=/tmp/uv-cache/
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/tmp
ENV PATH=/tmp/.local/bin:$PATH

WORKDIR ${LAMBDA_TASK_ROOT}

COPY stactools-item-generator/runtime/pyproject.toml pyproject.toml
COPY stactools-item-generator/runtime/src/stactools_item_generator/ ${LAMBDA_TASK_ROOT}/stactools_item_generator/

RUN uv export --no-dev --no-editable -o requirements.txt && \
  uv pip install --target ${LAMBDA_TASK_ROOT} -r requirements.txt && \
  uv tool install --with requests stactools;

CMD ["stactools_item_generator.handler.handler"]
