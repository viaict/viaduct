FROM python:3.6

RUN apt-get update && apt-get install -y node npm
RUN pip install uwsgi

WORKDIR /app

COPY package.json /app
RUN npm install

COPY requirements.txt /app
RUN pip install -r requirements.txt
