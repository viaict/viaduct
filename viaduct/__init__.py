import os

from flask import Flask, request
from flask.ext.babel import Babel
from flask.ext.login import LoginManager, current_user
from flask.ext.sqlalchemy import SQLAlchemy
from config import LANGUAGES
from viaduct.utilities import import_module


def is_module(path):
    init_path = os.path.join(path, '__init__.py')

    if os.path.isdir(path) and os.path.exists(init_path):
        return True
    elif os.path.isfile(path) and os.path.splitext(path)[1] == '.py':
        return True

    return False


def register_views(application, path, extension=''):
    application_path = os.path.dirname(os.path.abspath(application.root_path))

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
@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    if current_user is not None and current_user.locale is not None and \
            not current_user.is_anonymous():
        print current_user
        return current_user.locale
    return request.accept_languages.best_match(LANGUAGES.keys())

# Set up the login manager, which is used to store the details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'user.sign_in'

# Set up the database.
db = SQLAlchemy(application)
db.Model.to_dict = model_to_dict

# Set jinja global variables
application.jinja_env.globals.update(enumerate=enumerate)

# Register the blueprints.
import api

path = os.path.dirname(os.path.abspath(__file__))

register_views(application, os.path.join(path, 'views'))

from viaduct.models import User

login_manager.anonymous_user = User.get_anonymous_user
