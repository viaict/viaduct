from flask import Flask, request, Markup, render_template, session
from flask.json import JSONEncoder as BaseEncoder
from flask_babel import Babel
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from flask_debugtoolbar import DebugToolbarExtension

from raven.contrib.flask import Sentry
from speaklater import _LazyString
from sqlalchemy import MetaData
from markdown import markdown
from flask_jsglue import JSGlue

import datetime
import json
import logging
import os


version = 'v2.8.1.2'


def static_url(url):
    return url + '?v=' + version


def is_module(path):
    init_path = os.path.join(path, '__init__.py')

    if os.path.isdir(path) and os.path.exists(init_path):
        return True
    elif os.path.isfile(path) and os.path.splitext(path)[1] == '.py':
        return True

    return False


def register_views(app, path, extension=''):
    app_path = os.path.dirname(os.path.abspath(app.root_path))

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        # Check if the current file is a module.
        if is_module(file_path):
            # Get the module name from the file path.
            module_name = os.path.splitext(file_path)[0]
            module_name = os.path.relpath(module_name, app_path)
            module_name = module_name.replace('/', '.')

            blueprint = getattr(import_module(module_name), 'blueprint', None)

            if blueprint:
                print(('{0} has been imported.'.format(module_name)))
                app.register_blueprint(blueprint)


# Set up the app and load the configuration file.
app = Flask(__name__)
js_glue = JSGlue(app)
app.config.from_object('config.Config')
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'cache'

cache = Cache(app)
toolbar = DebugToolbarExtension(app)

if not app.debug and 'SENTRY_DSN' in app.config:
    sentry = Sentry(app)
    sentry.client.release = version


# Set up Flask Babel, which is used for internationalisation support.
babel = Babel(app)


@babel.localeselector
def get_locale():
    languages = app.config['LANGUAGES'].keys()
    # Try to look-up an session set for language
    lang = session.get('lang')
    if lang and lang in languages:
        return lang

    # if a user is logged in, use the locale from the user settings
    if current_user.is_authenticated and current_user.locale is not None:
        return current_user.locale

    return request.accept_languages.best_match(list(languages), default='nl')


class JSONEncoder(BaseEncoder):
    """Custom JSON encoding."""

    def default(self, o):
        if isinstance(o, _LazyString):
            # Lazy strings need to be evaluation.
            return str(o)

        return BaseEncoder.default(self, o)


@app.context_processor
def inject_urls():
    return dict(
        request_path=request.path,
        request_base_url=request.base_url,
        request_url=request.url,
        request_url_root=request.url_root)


app.json_encoder = JSONEncoder

# Set up the login manager, which is used to store the details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.sign_in'

# Set up the database.
constraint_naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Custom SQLAlchemy object that uses naming conventions.
# https://stackoverflow.com/questions/29153930/
db = SQLAlchemy(
    app, metadata=MetaData(naming_convention=constraint_naming_convention))

from app.utils import import_module, serialize_sqla  # noqa
from app.utils.thumb import thumb  # noqa
from app.utils.user import UserAPI  # noqa
from app.utils.company import CompanyAPI  # noqa
from app.utils.guide import GuideAPI  # noqa
from app.utils.module import ModuleAPI  # noqa
from app.forms.util import FormWrapper  # noqa
# Set jinja global variables
app.jinja_env.globals.update(enumerate=enumerate)
app.jinja_env.globals.update(render_template=render_template)
app.jinja_env.globals.update(markdown=markdown)
app.jinja_env.globals.update(Markup=Markup)
app.jinja_env.globals.update(UserAPI=UserAPI)
app.jinja_env.globals.update(CompanyAPI=CompanyAPI)
app.jinja_env.globals.update(GuideAPI=GuideAPI)
app.jinja_env.globals.update(ModuleAPI=ModuleAPI)
app.jinja_env.globals.update(datetime=datetime)
app.jinja_env.globals.update(json=json)
app.jinja_env.globals.update(serialize_sqla=serialize_sqla)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(thumb=thumb)
app.jinja_env.globals.update(isinstance=isinstance)
app.jinja_env.globals.update(list=list)
app.jinja_env.globals.update(static_url=static_url)
app.jinja_env.globals.update(get_locale=get_locale)
app.jinja_env.globals.update(app_config=app.config)
app.jinja_env.globals.update(FormWrapper=FormWrapper)

# Register the blueprints.
from . import api  # noqa

path = os.path.dirname(os.path.abspath(__file__))

register_views(app, os.path.join(path, 'views'))

from app.utils.template_filters import *  # noqa

from app.models.user import AnonymousUser  # noqa
login_manager.anonymous_user = AnonymousUser

log = logging.getLogger('werkzeug')
log.setLevel(app.config['LOG_LEVEL'])
