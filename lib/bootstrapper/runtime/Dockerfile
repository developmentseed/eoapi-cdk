ARG PYTHON_VERSION=3.11

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

ARG PGSTAC_VERSION
RUN echo "Using PGSTAC Version ${PGSTAC_VERSION}"

WORKDIR /tmp
RUN python -m pip install pip -U
RUN python -m pip install httpx psycopg["binary,pool"] pypgstac==${PGSTAC_VERSION} -t /asset

COPY runtime/handler.py /asset/handler.py

# https://stackoverflow.com/a/61746719
# Tip from eoAPI: turns out, asyncio is part of python
RUN rm -rf /asset/asyncio*

# A command must be present avoid the following error on CDK deploy:
# Error response from daemon: No command specified
CMD [ "echo", "ready to go!" ]
