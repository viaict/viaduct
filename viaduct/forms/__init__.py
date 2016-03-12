import os

from flask.ext.wtf import Form

from viaduct import app
from viaduct.utilities import import_module


def register_forms(path):
    app_path = os.path.dirname(os.path.abspath(app.root_path))

    for filename in os.listdir(path):

        if filename[-3:] != ".py":
            continue

        file_path = os.path.join(path, filename)

        name = os.path.splitext(file_path)[0]
        name = os.path.relpath(name, app_path)
        name = name.replace('/', '.')

        module = import_module(name)

        for name in dir(module):
            attribute = getattr(module, name)

            try:
                if not issubclass(attribute, Form):
                    continue
            except TypeError:
                continue

            globals()[name] = attribute

register_forms(os.path.dirname(os.path.abspath(__file__)))
