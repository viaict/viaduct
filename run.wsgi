import logging
import os
import sys

logging.basicConfig(stream=sys.stderr)

os.chdir(os.path.dirname(__file__))
#sys.path.append(os.path.dirname(__file__))

from viaduct import application

