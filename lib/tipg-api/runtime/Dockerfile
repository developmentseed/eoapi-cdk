ARG PYTHON_VERSION
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:${PYTHON_VERSION}

WORKDIR /tmp
RUN python -m pip install pip -U

COPY tipg-api/runtime/requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt "mangum>=0.14,<0.15" -t /asset --no-binary pydantic

# Reduce package size and remove useless files
RUN cd /asset && find . -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-[0-9]*//'); cp $f $n; done;
RUN cd /asset && find . -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN cd /asset && find . -type f -a -name '*.py' -print0 | xargs -0 rm -f
RUN find /asset -type d -a -name 'tests' -print0 | xargs -0 rm -rf

COPY tipg-api/runtime/src/*.py /asset/
COPY utils/utils.py /asset/

CMD ["echo", "hello world"]
