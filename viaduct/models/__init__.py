import os

from viaduct import application, db
from viaduct.utilities import import_module

def register_models(path):
	application_path = os.path.dirname(os.path.abspath(application.root_path))

	for filename in os.listdir(path):
		file_path = os.path.join(path, filename)

		name = os.path.splitext(file_path)[0]
		name = os.path.relpath(name, application_path)
		name = name.replace('/', '.')

		module = import_module(name)

		for name in dir(module):
			attribute = getattr(module, name)

			try:
				if not issubclass(attribute, db.Model):
					continue
			except TypeError:
				continue

			globals()[name] = attribute

register_models(os.path.dirname(os.path.abspath(__file__)))

