ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /tmp
COPY stac-auth-proxy/runtime/uv.lock stac-auth-proxy/runtime/pyproject.toml ./
COPY stac-auth-proxy/runtime/src/ ./src/

RUN <<EOF
uv export --locked --no-editable --no-dev --format requirements.txt -o requirements.txt
uv pip install \
  --compile-bytecode \
  --no-binary pydantic \
  --target /asset \
  --no-cache-dir \
  --disable-pip-version-check \
  -r requirements.txt
EOF
