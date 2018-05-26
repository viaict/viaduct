#!/bin/bash
set -e

rm -f config.py
ln -s secrets/master.py config.py
cat common_config.rb deploy_config.rb > config.rb

python manage.py db upgrade
uwsgi --ini uwsgi.ini
