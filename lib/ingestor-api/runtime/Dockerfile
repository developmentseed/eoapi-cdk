ARG PYTHON_VERSION

FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp

RUN yum install -y git

RUN python -m pip install pip -U

COPY runtime/requirements.txt requirements.txt

ARG PGSTAC_VERSION=0.9.5
RUN echo "pypgstac==${PGSTAC_VERSION}" > constraints.txt
RUN python -m pip install -r requirements.txt -c constraints.txt "mangum>=0.14,<0.15" -t /asset --no-binary pydantic

RUN mkdir -p /asset/src
COPY runtime/src/*.py /asset/src/

CMD ["echo", "hello world"]
