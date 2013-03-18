import os

from flask import Flask
from flask.ext.babel import Babel
from flask.ext.login import LoginManager
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

def import_module(name):
	print('Importing {0}...'.format(name))
	module = __import__(name.split('.')[0])

	print(module)

	for component in name.split('.')[1:]:
		print(component)
		module = getattr(module, component)

	return module

def register_blueprints(application, path, extension):
	path = os.path.relpath(path)

	for current, directories, files in os.walk(path):
		for directory in directories:
			here = os.path.dirname(os.path.abspath(__file__))
			here = os.path.dirname(os.path.abspath(here))
			current = os.path.relpath(current, here)
			current = current.replace('/', '.')
			name = '.'.join([current, directory, extension])
			#blueprint = getattr(import_module(name), 'blueprint', None)
			blueprint = None

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

# Set up support for REST APIs.
api_manager = Api(application)

# Set up the database.
db = SQLAlchemy(application)
db.Model.to_dict = model_to_dict

# Register the blueprints.
path = os.path.dirname(os.path.abspath(__file__))
register_blueprints(application, os.path.join(path, 'blueprints'), 'views')

import api

from viaduct.blueprints.user.views import load_anonymous_user

login_manager.anonymous_user = load_anonymous_user

