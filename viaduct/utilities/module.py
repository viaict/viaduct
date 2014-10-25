import sys


def import_module(name, globals=globals(), locals=locals(), fromlist=[],
                  level=-1):
    __import__(name)

    return sys.modules[name]
