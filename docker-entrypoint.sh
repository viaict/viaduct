#!/bin/bash

# Exit on error
set -e

cd /app

pip-sync

rm -f config.py
if [ $ENVIRONMENT = "prod" ]; then
	ln -s 'secrets/master.py' 'config.py'
elif [ $ENVIRONMENT = "dev" ]; then
	ln -s 'secrets/develop.py' 'config.py'
else
	ln -s 'secrets/local.py' 'config.py'
fi

echo 'Applying database migrations...'
python manage.py db upgrade

echo 'Starting server'
if [ $ENVIRONMENT = 'prod' -o $ENVIRONMENT = 'dev' ]; then
	uwsgi --ini viaduct-master.ini
else
	./watch.sh
fi
