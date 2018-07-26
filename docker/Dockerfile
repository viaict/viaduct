FROM python:3.6-alpine AS development
WORKDIR /app

# Ruby
RUN apk add -U ruby ruby-rdoc ruby-bundler ruby-irb
COPY Gemfile /app
RUN bundle install

# Node
RUN apk add -U nodejs npm
COPY package.json /app
RUN npm install -g grunt-cli clientjade jshint
RUN npm install

# Python
RUN apk add -U postgresql-libs git libmagic libjpeg-turbo bash pcre
RUN pip install --upgrade pip pip-tools

# Install a virtual package with build dependencies voor pip install
RUN apk add -U --virtual build-deps \
    python3-dev build-base linux-headers pcre-dev musl-dev \
    postgresql-dev libffi-dev libjpeg-turbo-dev libressl-dev zlib-dev

COPY requirements.in requirements.txt ./
RUN pip-sync && \
    pip install uwsgi && \
    pip install -r requirements.txt && \
    pip install -r requirements.txt

# Remove virtual package
RUN apk del build-deps


FROM development AS production

# Copy the source into the image for production
COPY src/ /app/src
RUN mkdir -p /app/src/js/global && \
    clientjade src/jade/ > src/js/global/jade.js

COPY . /app
RUN cat common_config.rb deploy_config.rb > config.rb
RUN grunt clean && grunt prod
RUN pybabel compile -d app/translations
RUN compass clean && compass compile
