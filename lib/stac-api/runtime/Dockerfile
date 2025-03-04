ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp
RUN python -m pip install pip -U

COPY stac-api/runtime/requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt "mangum>=0.14,<0.15" -t /asset --no-binary pydantic

RUN mkdir -p /asset/src
COPY stac-api/runtime/src/*.py /asset/
COPY utils/utils.py /asset/

CMD ["echo", "hello world"]
