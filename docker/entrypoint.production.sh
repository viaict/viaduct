#!/bin/bash
set -e

python manage.py db upgrade
uwsgi --ini docker/uwsgi.ini
