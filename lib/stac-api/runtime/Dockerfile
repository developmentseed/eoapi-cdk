ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp
RUN python -m pip install pip -U

ARG STAC_FASTAPI_VERSION=2.4.8
COPY runtime/requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt \
  stac-fastapi.api==${STAC_FASTAPI_VERSION} \
  stac-fastapi.extensions==${STAC_FASTAPI_VERSION} \
  stac-fastapi.pgstac==${STAC_FASTAPI_VERSION} \
  stac-fastapi.types==${STAC_FASTAPI_VERSION} \
  "mangum>=0.14,<0.15" \
  -t /asset --no-binary pydantic

RUN mkdir -p /asset/src
COPY runtime/src/*.py /asset/src/

CMD ["echo", "hello world"]