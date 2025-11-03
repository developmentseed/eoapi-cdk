ARG PYTHON_VERSION=3.12
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /tmp

COPY stac-loader/runtime/pyproject.toml stac-loader/runtime/uv.lock ./
COPY stac-loader/runtime/src/ ./src/

ARG PGSTAC_VERSION=0.9.6

RUN <<EOF
uv add --no-sync pypgstac==${PGSTAC_VERSION}
uv export --locked --no-editable --no-dev --format requirements.txt -o requirements.txt
uv pip install \
  --compile-bytecode \
  --target /asset \
  --no-cache-dir \
  --disable-pip-version-check \
  -r requirements.txt
EOF

CMD ["stac_loader.handler.handler"]
