FROM python:alpine AS development
WORKDIR /app

# Ruby
RUN apk add -U ruby ruby-rdoc ruby-bundler ruby-irb
COPY Gemfile /app
RUN bundle install

# Node
RUN apk add -U nodejs yarn
COPY package.json /app
RUN npm install -g grunt-cli clientjade jshint
RUN npm install

# Python
RUN apk add -U postgresql-libs git libmagic libjpeg-turbo bash pcre
COPY requirements.in requirements.txt ./
RUN pip install --upgrade pip pip-tools

RUN apk add -U --virtual build-deps \
    python3-dev build-base linux-headers pcre-dev musl-dev \
    postgresql-dev libffi-dev libjpeg-turbo-dev libressl-dev zlib-dev

RUN pip-sync && \
    pip install uwsgi && \
    pip install -r requirements.txt && \
    pip install -r requirements.txt

RUN apk del build-deps


FROM development AS production

# Copy the source into the image for production
COPY . /app

RUN mkdir -p /app/src/js/global && \
    clientjade src/jade/ > src/js/global/jade.js

RUN grunt clean && grunt prod
RUN pybabel compile -d app/translations
RUN compass clean && compass compile
