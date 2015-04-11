#!venv/bin/python
import os
pybabel = 'venv/bin/pybabel'
os.system(pybabel + ' extract -F babel.cfg -k lazy_gettext -o messages.pot \
          viaduct')
os.system(pybabel + ' init -i messages.pot -d viaduct/translations -l en')
os.system(pybabel + ' init -i messages.pot -d viaduct/translations -l nl')
os.remove('messages.pot')
