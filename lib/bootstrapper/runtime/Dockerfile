FROM lambci/lambda:build-python3.8

WORKDIR /tmp

RUN pip install httpx psycopg[binary,pool] pypgstac==0.6.13 -t /asset

COPY runtime/handler.py /asset/handler.py

# https://stackoverflow.com/a/61746719
# Tip from eoAPI: turns out, asyncio is part of python
RUN rm -rf /asset/asyncio*

# A command must be present avoid the following error on CDK deploy:
# Error response from daemon: No command specified
CMD [ "echo", "ready to go!" ]