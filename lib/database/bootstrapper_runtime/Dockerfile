ARG PYTHON_VERSION
FROM lambci/lambda:build-python${PYTHON_VERSION}

ARG PGSTAC_VERSION
RUN echo "PGSTAC_VERSION: ${PGSTAC_VERSION}"
RUN echo "PYTHON_VERSION: ${PYTHON_VERSION}"

WORKDIR /tmp

RUN pip install httpx psycopg[binary,pool] pypgstac==${PGSTAC_VERSION} -t /asset

COPY bootstrapper_runtime/handler.py /asset/handler.py

# https://stackoverflow.com/a/61746719
# Tip from eoAPI: turns out, asyncio is part of python
RUN rm -rf /asset/asyncio*

# A command must be present avoid the following error on CDK deploy:
# Error response from daemon: No command specified
CMD [ "echo", "ready to go!" ]