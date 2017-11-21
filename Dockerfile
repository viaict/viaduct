FROM python:3.6

RUN apt-get update && apt-get install -y node npm ruby
RUN pip install uwsgi

WORKDIR /app

COPY Gemfile /app
RUN gem install bundler && bundle install

COPY package.json /app
RUN npm install -g grunt-cli jshint
RUN npm install

COPY requirements.txt /app
RUN pip install -r requirements.txt
