FROM python:3.8

COPY . /app

WORKDIR /app

RUN apt-get update &&\
    apt-get install -y python3-pip &&\
    pip install -r requirements.txt
