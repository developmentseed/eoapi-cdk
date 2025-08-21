ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp
RUN python -m pip install pip -U

# Install system dependencies to compile (numexpr)
RUN dnf install -y gcc-c++ findutils

COPY titiler-pgstac-api/runtime/requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt "mangum>=0.14,<0.15" -t /asset

# copy libexpat.so.1 into a location included in LD_LIBRARY_PATH in the Lambda runtime environment
# (/usr/lib64 is not available in the Lambda runtime, just the build environment)
RUN cp /usr/lib64/libexpat.so.1 /asset/

# Remove system dependencies
RUN dnf remove -y gcc-c++

# Reduce package size and remove useless files
RUN find /asset -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[0-9]*//'); cp $f $n; done;
RUN find /asset -type d -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find /asset -type f -name '*.py' -print0 | xargs -0 rm -f
RUN find /asset -type d -name 'tests' -print0 | xargs -0 rm -rf
RUN rm -rdf /asset/numpy/doc/ /asset/boto3* /asset/botocore* /asset/bin /asset/geos_license /asset/Misc

# Strip debug symbols from compiled C/C++ code (except for numpy.libs!)
RUN cd /asset && \
  find . -type f -name '*.so*' \
  -not -path "./numpy.libs/*" \
  -exec strip --strip-unneeded {} \;

COPY titiler-pgstac-api/runtime/src/*.py /asset/
COPY utils/utils.py /asset/

CMD ["echo", "hello world"]
