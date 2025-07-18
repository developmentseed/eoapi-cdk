ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp
RUN python -m pip install pip -U

COPY stac-auth-proxy/runtime/requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt "mangum>=0.14,<0.15" -t /asset

RUN mkdir -p /asset/src
COPY stac-auth-proxy/runtime/src/*.py /asset/

CMD ["echo", "hello world"]
