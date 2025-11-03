ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /tmp
COPY titiler-pgstac-api/runtime/uv.lock titiler-pgstac-api/runtime/pyproject.toml ./
COPY titiler-pgstac-api/runtime/src/ ./src/
COPY utils/utils.py /asset/

RUN <<EOF
dnf install -y gcc-c++ findutils
uv export --locked --no-editable --no-dev --format requirements.txt -o requirements.txt
uv pip install \
  --compile-bytecode \
  --no-binary pydantic \
  --target /asset \
  --no-cache-dir \
  --disable-pip-version-check \
  -r requirements.txt

# copy libexpat.so.1 into a location included in LD_LIBRARY_PATH in the Lambda runtime environment
# (/usr/lib64 is not available in the Lambda runtime, just the build environment)
cp /usr/lib64/libexpat.so.1 /asset/
EOF

# Reduce package size and remove useless files
WORKDIR /asset
RUN <<EOF
find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[0-9]*//'); cp $f $n; done;
find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
find . -type d -a -name 'tests' -print0 | xargs -0 rm -rf

# remove boto3, botocore (in favor of versions pre-installed in Lambda runtime) and other misc files
rm -rdf /asset/numpy/doc/ /asset/boto3* /asset/botocore* /asset/bin /asset/geos_license /asset/Misc

# Strip debug symbols from compiled C/C++ code (except for numpy.libs!)
find . -type f -name '*.so*' \
  -not -path "./numpy.libs/*" \
  -exec strip --strip-unneeded {} \;

EOF

CMD ["echo", "hello world"]
