import logging
import os

from flask import Flask, request, session
from flask.json import JSONEncoder as BaseEncoder
from flask_babel import Babel
from flask_login import current_user
from speaklater import _LazyString

from app.roles import Roles
from app.utils.import_module import import_module
from .extensions import db, login_manager, \
    cache, toolbar, jsglue, sentry

version = 'v2.9.1.0'


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
app.config.from_object('config.Config')

# Set up Flask Babel, which is used for internationalisation support.
babel = Babel(app)

app.path = os.path.dirname(os.path.abspath(__file__))


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


# Has to be imported *after* app is created and Babel is initialised
from app.models.user import AnonymousUser  # noqa
from app import jinja_env  # noqa


def init_app():
    app.config['CACHE_TYPE'] = 'filesystem'
    app.config['CACHE_DIR'] = 'cache'

    logging.basicConfig()

    cache.init_app(app)
    toolbar.init_app(app)
    jsglue.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'user.sign_in'

    db.init_app(app)

    if not app.debug and 'SENTRY_DSN' in app.config:
        sentry.init_app(app)
        sentry.client.release = version

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

    @app.context_processor
    def inject_seo_write_permission():
        from app.service import role_service
        can_write_seo = role_service.user_has_role(current_user,
                                                   Roles.SEO_WRITE)
        return dict(can_write_seo=can_write_seo)

    app.json_encoder = JSONEncoder

    register_views(app, os.path.join(app.path, 'views'))

    login_manager.anonymous_user = AnonymousUser

    log = logging.getLogger('werkzeug')
    log.setLevel(app.config['LOG_LEVEL'])
