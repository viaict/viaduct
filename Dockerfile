FROM python:3.6

RUN apt-get update && apt-get install -y

WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
RUN pip install uwsgi
