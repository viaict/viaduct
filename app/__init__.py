import datetime
import logging
import os
import sys

import connexion
from flask import Flask, request, session
from flask.json import JSONEncoder as BaseEncoder
from flask_babel import Babel
from flask_login import current_user
from flask_swagger_ui import get_swaggerui_blueprint
from speaklater import _LazyString  # noqa
from hashfs import HashFS
import mimetypes

from app.exceptions import ResourceNotFoundException, ValidationException, \
    AuthorizationException
from app.roles import Roles
from app.utils.import_module import import_module
from .connexion_app import ConnexionFlaskApp
from .extensions import db, login_manager, \
    cache, toolbar, jsglue, sentry, oauth, cors

version = 'v2.10.0.8'

app = Flask(__name__)
app.config.from_object('config.Config')

logging.basicConfig(
    format='[%(asctime)s] %(levelname)7s [%(name)s]: %(message)s',
    stream=sys.stdout,
)

app.logger_name = 'app.flask'
app.logger.setLevel(logging.NOTSET)

_logger = logging.getLogger('app')
_logger.setLevel(app.config['LOG_LEVEL'])

logging.getLogger('werkzeug').setLevel(logging.INFO)


# Set up Flask Babel, which is used for internationalisation support.
babel = Babel(app)

hashfs = HashFS(app.config['HASHFS_ROOT_DIR'])
mimetypes.init()

app.path = os.path.dirname(os.path.abspath(__file__))


def static_url(url):
    return url + '?v=' + version


def is_module(path):
    init_path = os.path.join(path, '__init__.py')

    if os.path.isdir(path) and os.path.exists(init_path):
        return True
    elif os.path.isfile(path) and os.path.splitext(path)[1] == '.py':
        return True

    return False


def register_views(app, path):
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
                _logger.info('"{}" has been imported'.format(module_name))
                app.register_blueprint(blueprint)


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

    cache.init_app(app)
    toolbar.init_app(app)
    jsglue.init_app(app)
    oauth.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    init_oauth()

    login_manager.init_app(app)
    login_manager.login_view = 'user.sign_in'

    db.init_app(app)

    if not app.debug and 'SENTRY_DSN' in app.config:
        sentry.init_app(app, logging=True, level=logging.ERROR)
        sentry.client.release = version

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

    @app.context_processor
    def inject_privacy_policy_url():
        if get_locale() == 'nl':
            url = app.config['PRIVACY_POLICY_URL_NL']
        else:
            url = app.config['PRIVACY_POLICY_URL_EN']

        return dict(privacy_policy_url=url)

    class JSONEncoder(BaseEncoder):
        """Custom JSON encoding."""

        def default(self, o):
            if isinstance(o, _LazyString):
                # Lazy strings need to be evaluation.
                return str(o)

            if isinstance(o, datetime.datetime):
                if o.tzinfo:
                    # eg: '2015-09-25T23:14:42.588601+00:00'
                    return o.isoformat('T')
                else:
                    # No timezone present (almost always in viaduct)
                    # eg: '2015-09-25T23:14:42.588601'
                    return o.isoformat('T')

            if isinstance(o, datetime.date):
                return o.isoformat()

            return BaseEncoder.default(self, o)
    app.json_encoder = JSONEncoder

    register_views(app, os.path.join(app.path, 'views'))

    login_manager.anonymous_user = AnonymousUser

    return get_patched_api_app()


def init_oauth():
    from app.service import user_service, oauth_service

    @oauth.clientgetter
    def oauth_clientgetter(client_id):
        return oauth_service.get_client_by_id(client_id)

    @oauth.grantgetter
    def oauth_grantgetter(client_id, code):
        return oauth_service.get_grant_by_client_id_and_code(client_id, code)

    @oauth.grantsetter
    def oauth_grantsetter(client_id, code, request, *_, **__):
        return oauth_service.create_grant(
            client_id, code, current_user.id, request)

    @oauth.tokengetter
    def oauth_tokengetter(access_token=None, refresh_token=None):
        return oauth_service.get_token(access_token, refresh_token)

    @oauth.tokensetter
    def oauth_tokensetter(token, request, *_, **__):
        user_id = request.user.id if request.user else current_user.id
        return oauth_service.create_token(token, user_id, request)

    @oauth.usergetter
    def oauth_usergetter(email, password, *_, **__):
        try:
            return user_service.get_user_by_login(
                email=email, password=password)
        except (ResourceNotFoundException, AuthorizationException,
                ValidationException):
            return None


def get_patched_api_app():
    # URL for exposing Swagger UI (without trailing '/')
    swagger_url = '/api/docs'

    # The API url defined by connexion.
    api_urls = [{"name": "pimpy", "url": "/api/pimpy/swagger.json"},
                {"name": "token", "url": "/api/token/swagger.json"}]

    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_urls[0]["url"],
        config={  # Swagger UI config overrides
            'app_name': "Study Association via - Public API documentation",
            'urls': api_urls
        },
        oauth_config={
            'clientId': "swagger",
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)

    def add_api(patched_app, name):
        kwargs = {
            "protocol": "http" if patched_app.app.debug else "https",
        }
        with open("./app/swagger/swagger-{}.yaml".format(name), "w") as f:
            a = patched_app.app.jinja_env \
                .get_template("swagger/{}.yaml"
                              .format(name)).render(**kwargs)
            f.write(a)

        patched_app.add_api(
            './swagger-{}.yaml'.format(name),
            base_path="/api/{}".format(name), validate_responses=True,
            resolver=connexion.RestyResolver('app.api.{}'.format(name)),
            pythonic_params=True, strict_validation=True)

    connexion_app = ConnexionFlaskApp(
        __name__, app, specification_dir='swagger/', swagger_ui=False)

    add_api(connexion_app, "pimpy")
    add_api(connexion_app, "token")
    return connexion_app
