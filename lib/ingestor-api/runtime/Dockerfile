ARG PYTHON_VERSION=3.12
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

WORKDIR /tmp

COPY runtime/pyproject.toml runtime/uv.lock ./

ARG PGSTAC_VERSION
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

RUN mkdir -p /asset/src
COPY runtime/src/*.py /asset/src/

CMD ["echo", "hello world"]
