#!venv/bin/python
import os
import sys
pybabel = 'venv/bin/pybabel'
os.system(pybabel + ' compile -d viaduct/translations')
