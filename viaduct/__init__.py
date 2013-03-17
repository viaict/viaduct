import os

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

def import_module(name):
	module = __import__(name)

	for component in name.split('.')[1:]:
		module = getattr(module, component)

	return module

def register_blueprints(application, path, extension):
	path = os.path.relpath(path)

	for current, directories, files in os.walk(path):
		for directory in directories:
			name = '.'.join([current.replace('/', '.'), directory, extension])
			print('Importing ' + name)
			blueprint = getattr(import_module(name), 'blueprint', None)

			if blueprint:
				application.register_blueprint(blueprint)

# Set up the application and load the configuration file.
application = Flask(__name__)
application.config.from_object('config')

# Set up the login manager, which is used to store the details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'signin'

# Set up the database.
db = SQLAlchemy(application)

# Register the blueprints.
path = os.path.dirname(os.path.abspath(__file__))
register_blueprints(application, os.path.join(path, 'blueprints'), 'views')

from viaduct.blueprints.user.views import blueprint

application.register_blueprint(blueprint)

#import group
#import navigation
#import page
#import user
#import upload
#import pimpy

from viaduct.blueprints.user.views import load_anonymous_user

login_manager.anonymous_user = load_anonymous_user

