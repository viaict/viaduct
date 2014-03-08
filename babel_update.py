#!venv/bin/python
import os
import sys
pybabel = 'venv/bin/pybabel'
os.system(pybabel +' extract -F babel.cfg -k lazy_gettext -o messages.pot \
          viaduct')
os.system(pybabel + ' update -i messages.pot -d viaduct/translations')
os.unlink('messages.pot')
