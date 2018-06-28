from app import app
from app.exceptions import ValidationException, AuthorizationException
from app.service import user_service

from flask import session, request

from functools import wraps
from collections import namedtuple
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


SAMLInfo = namedtuple('SAMLInfo', ['auth', 'req'])


def _requires_saml_data(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'saml_data' not in session:
            session['saml_data'] = {}

        response = f(*args, **kwargs)

        # Explicitly tell the session that it has been modified,
        # since just adding/removing an item in the session['saml_data']
        # dict is not picked up as no items in the session dict itself
        # are changed. See:
        # http://flask.pocoo.org/docs/1.0/api/?highlight=session#flask.session
        session.modified = True

        return response

    return wrapper


def ensure_data_cleared(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        finally:
            clear_saml_data()

    return wrapper


def build_saml_info():
    url_data = urlparse(request.url)

    saml_req = {
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'https': 'on'
    }

    saml_path = app.config['SAML_PATH']
    saml_auth = OneLogin_Saml2_Auth(saml_req, custom_base_path=saml_path)

    return SAMLInfo(saml_auth, saml_req)


@_requires_saml_data
def process_response(saml_info):
    saml_auth = saml_info.auth

    saml_auth.process_response()
    errors = saml_auth.get_errors()

    if errors:
        raise ValidationException(
            'One or more errors occurred during SAML response processing: {}'
            .format(saml_auth.get_last_error_reason()))

    if saml_auth.is_authenticated():
        session['saml_data']['is_authenticated'] = True
        session['saml_data']['attributes'] = saml_auth.get_attributes()
        session['saml_data']['nameid'] = saml_auth.get_nameid()
    else:
        session['saml_data']['is_authenticated'] = False


def get_relaystate_redirect_url(saml_info, fallback_url):
    saml_auth = saml_info.auth

    if 'RelayState' in request.form and \
            OneLogin_Saml2_Utils.get_self_url(saml_info.req) \
            != request.form['RelayState']:
        return saml_auth.redirect_to(request.form['RelayState'])

    return fallback_url


def initiate_login(saml_info, return_to, force_authn=False):
    return saml_info.auth.login(return_to=return_to, force_authn=force_authn)


def build_metadata(saml_info):
    settings = saml_info.auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        return metadata, \
            {'Content-Type': 'application/xml',
             'Content-Disposition': 'inline; filename="metadata.xml"'}
    else:
        raise ValidationException(
            'Errors occurred when building SAML metadata: {}'.format(
                ', '.join(errors)))


@_requires_saml_data
def set_redirect_url(redirect_url):
    session['saml_data']['redirect_url'] = redirect_url


@_requires_saml_data
def get_redirect_url(fallback_url):
    return session['saml_data'].get('redirect_url', fallback_url)


@_requires_saml_data
def user_is_authenticated():
    return session['saml_data'].get('is_authenticated', False)


@_requires_saml_data
def get_attributes():
    return session['saml_data'].get('attributes', {})


def get_user_by_uid():
    attributes = get_attributes()
    uid = attributes.get('urn:mace:dir:attribute-def:uid')
    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    user = user_service.get_user_by_student_id(uid)

    if user.disabled:
        raise AuthorizationException("User is disabled.")

    return user


@_requires_saml_data
def get_nameid():
    return session['saml_data'].get('nameid')


@_requires_saml_data
def clear_saml_data():
    del session['saml_data']
