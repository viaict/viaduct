#!/bin/bash
set -e

CLIENTJADE=$(which clientjade)
GRUNT=$(which grunt)

rm -f config.py
if [ $ENVIRONMENT = "prod" ]; then
    echo 'STARTING PRODUCTION SERVER'
    ln -s 'secrets/master.py' 'config.py'
  cat common_config.rb deploy_config.rb > config.rb
elif [ $ENVIRONMENT = "dev" ]; then
    echo 'STARTING DEVELOPMENT SERVER'
    ln -s 'secrets/develop.py' 'config.py'
    cat common_config.rb > config.rb
else
    echo 'STARTING DEVELOPMENT SERVER'
    ln -s 'secrets/local.py' 'config.py'
    cat common_config.rb > config.rb
fi

echo 'Compiling Jade templates'
mkdir -p /app/src/js/global
nodejs $CLIENTJADE src/jade/ > src/js/global/jade.js

echo 'Compiling scss'
compass clean
compass compile

echo 'Compiling assets'
nodejs $GRUNT clean
nodejs $GRUNT prod

echo 'Compiling translations'
pybabel compile -d app/translations > /dev/null

echo 'Applying database migrations'
python manage.py db upgrade

echo 'Starting server'
if [[ $ENVIRONMENT == 'prod' || $ENVIRONMENT == 'dev' ]]; then
    uwsgi --ini viaduct-master.ini
else
    ./watch.sh
fi
