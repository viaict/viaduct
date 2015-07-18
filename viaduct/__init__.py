import os

from flask import Flask, request, Markup, render_template
from flask.ext.babel import Babel
from flask.ext.login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy as BaseSQLAlchemy, Model, \
    _BoundDeclarativeMeta, _QueryProperty, declarative_base
from sqlalchemy import MetaData
from config import LANGUAGES
from viaduct.utilities import import_module, serialize_sqla
from markdown import markdown
import datetime
import json


version = 'v2.2.0.3'


def static_url(url):
    return url + '?v=' + version


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
                print(('{0} has been imported.'.format(module_name)))
                application.register_blueprint(blueprint)


# Set up the application and load the configuration file.
application = Flask(__name__)
application.config.from_object('config')

# Set up Flask Babel, which is used for internationalisation support.
babel = Babel(application)


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    if current_user and not current_user.is_anonymous() \
            and current_user.locale is not None:
        return current_user.locale

    # Try to look-up an cookie set for language
    lang = request.cookies.get('lang')
    if lang and lang in LANGUAGES.keys():
        return lang
    else:
        return request.accept_languages.best_match(list(LANGUAGES.keys()))

# Set up the login manager, which is used to store the details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'user.sign_in'

# Set up the database.
constraint_naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class SQLAlchemy(BaseSQLAlchemy):
    """ Custom SQLAlchemy object that uses naming conventions.
    https://stackoverflow.com/questions/29153930/

    With Flask-SQLAlchemy 2.1 this can be done better, but it is not released
    yet. And 2.0 caused issues because of autoflush so those should be fixed.
    """
    def make_declarative_base(self):
        metadata = MetaData(naming_convention=constraint_naming_convention)

        base = declarative_base(metadata=metadata, cls=Model, name='Model',
                                metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base

db = SQLAlchemy(application)

from viaduct.api.user import UserAPI
from viaduct.api.company import CompanyAPI
from viaduct.api.guide import GuideAPI
from viaduct.api.module import ModuleAPI
from viaduct.helpers.thumb import thumb

# Set jinja global variables
application.jinja_env.globals.update(enumerate=enumerate)
application.jinja_env.globals.update(render_template=render_template)
application.jinja_env.globals.update(markdown=markdown)
application.jinja_env.globals.update(Markup=Markup)
application.jinja_env.globals.update(UserAPI=UserAPI)
application.jinja_env.globals.update(CompanyAPI=CompanyAPI)
application.jinja_env.globals.update(GuideAPI=GuideAPI)
application.jinja_env.globals.update(ModuleAPI=ModuleAPI)
application.jinja_env.globals.update(datetime=datetime)
application.jinja_env.globals.update(json=json)
application.jinja_env.globals.update(serialize_sqla=serialize_sqla)
application.jinja_env.globals.update(len=len)
application.jinja_env.globals.update(thumb=thumb)
application.jinja_env.globals.update(isinstance=isinstance)
application.jinja_env.globals.update(list=list)

application.jinja_env.globals.update(static_url=static_url)
application.jinja_env.globals.update(get_locale=get_locale)

# Register the blueprints.
from . import api  # noqa

path = os.path.dirname(os.path.abspath(__file__))

register_views(application, os.path.join(path, 'views'))

from viaduct.models import User

login_manager.anonymous_user = User.get_anonymous_user
