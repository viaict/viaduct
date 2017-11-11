#!/bin/sh

# Exit on error
set -e

cd /app

echo 'Applying database migrations...'
python manage.py db upgrade

echo 'Starting server'
uwsgi --ini viaduct-master.ini