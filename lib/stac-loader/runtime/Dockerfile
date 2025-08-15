ARG PYTHON_VERSION=3.12
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /asset

COPY stac-loader/runtime/pyproject.toml pyproject.toml
COPY stac-loader/runtime/src/stac_loader/ stac_loader/

ARG PGSTAC_VERSION=0.9.6
RUN uv add --no-sync pypgstac==${PGSTAC_VERSION} && \
  uv export --no-dev --no-editable -o requirements.txt && \
  uv pip install --target /asset -r requirements.txt

CMD ["stac_loader.handler.handler"]
