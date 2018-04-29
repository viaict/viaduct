#!/bin/bash
set -e

rm -f config.py
ln -s secrets/local.py config.py
cat common_config.rb > config.rb

bash watch.sh
