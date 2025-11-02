ARG PYTHON_VERSION=3.12
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_CACHE_DIR=/tmp/uv-cache/
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/tmp
ENV PATH=/tmp/.local/bin:$PATH

WORKDIR /tmp

COPY stactools-item-generator/runtime/pyproject.toml stac-loader/runtime/uv.lock ./
COPY stactools-item-generator/runtime/src/ ./src/

RUN <<EOF
dnf install -y git && dnf clean all && rm -rf /var/cache/dnf
uv export --no-dev --no-editable -o requirements.txt
uv pip install --target ${LAMBDA_TASK_ROOT} -r requirements.txt
uv tool install --with "numpy<2.3.0",requests stactools;
EOF

CMD ["stactools_item_generator.handler.handler"]
