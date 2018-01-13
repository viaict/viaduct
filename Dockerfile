FROM python:3.6

RUN apt-get update && apt-get install -y node npm ruby

WORKDIR /app

COPY Gemfile /app
RUN gem install bundler && bundle install

COPY package.json /app
RUN npm install -g grunt-cli clientjade jshint
RUN npm install

COPY requirements.txt /app
RUN pip install pip-tools
RUN pip-sync
RUN pip install uwsgi

COPY . /app
