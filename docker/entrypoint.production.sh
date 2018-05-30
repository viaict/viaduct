#!/bin/bash
set -e

python manage.py db upgrade
uwsgi --ini uwsgi.ini
