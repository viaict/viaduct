#!/bin/bash
set -e

rm -f config.py
ln -s secrets/master.py config.py

python manage.py db upgrade
uwsgi --ini uwsgi.ini
