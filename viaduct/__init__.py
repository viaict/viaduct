import os
import sys

from flask import Flask
from flask.ext.babel import Babel
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

def get_application_path():
	application_path = application.root_path
	application_path = os.path.dirname(os.path.abspath(application_path))

	return application_path

def is_module(path):
	init_path = os.path.join(path, '__init__.py')

	if os.path.isdir(path) and os.path.exists(init_path):
		return True
	elif os.path.isfile(path) and os.path.splitext(path)[1] == '.py':
		return True

	return False

def import_module(module_name):
	try:
		__import__(module_name)
	except ImportError:
		return None

	return sys.modules[module_name]

def register_views(application, path, extension=''):
	application_path = get_application_path()

	for filename in os.listdir(path):
		file_path = os.path.join(path, filename)

		# Check if the current file is a module.
		if is_module(file_path):
			# Get the module name from the file path.
			module_name = os.path.splitext(file_path)[0]
			module_name = os.path.relpath(module_name, application_path)
			module_name = module_name.replace('/', '.')

			blueprint = getattr(import_module(module_name), 'blueprint', None)

			if blueprint:
				print('{0} has been imported.'.format(module_name))
				application.register_blueprint(blueprint)

def register_blueprints(application, path, extension):
	path = os.path.relpath(path)

	for current, directories, files in os.walk(path):
		for directory in directories:
			here = os.path.dirname(os.path.abspath(__file__))
			here = os.path.dirname(os.path.abspath(here))
			current = os.path.relpath(current, here)
			current = current.replace('/', '.')
			name = '.'.join([current, directory, extension])
			blueprint = getattr(import_module(name), 'blueprint', None)

			if blueprint:
				application.register_blueprint(blueprint)

def model_to_dict(self):
	result = {}

	for column in self.__table__.columns:
		result[column.name] = getattr(self, column.name)

	return result

# Set up the application and load the configuration file.
application = Flask(__name__)
application.config.from_object('config')

# Set up Flask Babel, which is used for internationalisation support.
babel = Babel(application)

# Set up the login manager, which is used to store the details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'signin'

# Set up the database.
db = SQLAlchemy(application)
db.Model.to_dict = model_to_dict

# Register the blueprints.
import api

path = os.path.dirname(os.path.abspath(__file__))

register_views(application, os.path.join(path, 'views'))
register_blueprints(application, os.path.join(path, 'blueprints'), 'views')

from viaduct.blueprints.user.views import load_anonymous_user

login_manager.anonymous_user = load_anonymous_user

