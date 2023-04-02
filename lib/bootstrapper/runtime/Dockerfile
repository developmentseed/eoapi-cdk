ARG PGSTAC_VERSION

FROM ghcr.io/stac-utils/pgstac:v${PGSTAC_VERSION}
# An ARG declared before a FROM is outside of a build stage, so it can’t be used in any instruction after a FROM
ARG PGSTAC_VERSION
RUN echo "Using PGSTAC Version ${PGSTAC_VERSION}"
ENV ENV=${ENV}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}

WORKDIR /tmp

RUN pip install boto3 requests psycopg[binary,pool] pypgstac==${PGSTAC_VERSION} -t /asset

COPY lib/bootstrapper/runtime/handler.py /asset/handler.py
COPY lib/bootstrapper/insert-test-data.py /asset/insert-test-data.py

# https://stackoverflow.com/a/61746719
# Tip from eoAPI
RUN rm -rf /asset/asyncio*

# A command must be present avoid the following error on CDK deploy:
# Error response from daemon
CMD [ "echo", "ready to go!" ]