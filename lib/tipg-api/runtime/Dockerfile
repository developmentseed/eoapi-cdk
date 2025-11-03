ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /tmp
COPY tipg-api/runtime/uv.lock tipg-api/runtime/pyproject.toml ./
COPY tipg-api/runtime/src/ ./src/
COPY utils/utils.py /asset/

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

# Reduce package size and remove useless files
WORKDIR /asset
RUN <<EOF
dnf install -y findutils && \
dnf clean all && \
rm -rf /var/cache/dnf
find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[0-9]*//'); cp $f $n; done;
find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
find . -type d -a -name 'tests' -print0 | xargs -0 rm -rf
EOF

CMD ["echo", "hello world"]
