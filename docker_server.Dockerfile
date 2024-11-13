# quote-search Dockfile
FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install -y python3 python3-pip \
    && pip3 install setuptools

RUN mkdir /server
COPY ./server /server
WORKDIR /server
RUN python3 -m pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--loop", "asyncio"]