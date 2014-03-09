#!venv/bin/python
import os
import sys
pybabel = 'venv/bin/pybabel'
if len(sys.argv) != 2:
    print "usage: babel_init <language-code>"
    sys.exit(1)
os.system(pybabel +' extract -F babel.cfg -k lazy_gettext -o messages.pot \
          viaduct')
os.system(pybabel +' init -i messages.pot -d viaduct/translations -l '
          + sys.argv[1])
os.unlink('messages.pot')
