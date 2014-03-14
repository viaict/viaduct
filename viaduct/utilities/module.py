import sys


def import_module(name, globals=globals(), locals=locals(), fromlist=[],
    level=-1):
    try:
        __import__(name)
    except ImportError:
        return None

    return sys.modules[name]
