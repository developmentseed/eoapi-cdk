FROM lambci/lambda:build-python3.8

ARG PGSTAC_VERSION
RUN echo "Using PGSTAC Version ${PGSTAC_VERSION}"

WORKDIR /tmp

RUN pip install requests psycopg[binary,pool] pypgstac==${PGSTAC_VERSION} -t /asset

COPY runtime/handler.py /asset/handler.py

# https://stackoverflow.com/a/61746719
# Tip from eoAPI: turns out, asyncio is part of python
RUN rm -rf /asset/asyncio*
