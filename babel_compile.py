#!venv/bin/python
import os
pybabel = 'venv/bin/pybabel'
os.system(pybabel + ' compile -d viaduct/translations')
