from app import app
from app.exceptions import ValidationException, AuthorizationException, \
    BusinessRuleException
from app.service import user_service

from flask import session, request
from flask_login import current_user

from functools import wraps
from collections import namedtuple
from urllib.parse import urlparse
from datetime import datetime as dt, timedelta

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


SAMLInfo = namedtuple('SAMLInfo', ['auth', 'req'])

SIGN_UP_SESSION_TIMEOUT = timedelta(minutes=5)


def _requires_saml_data(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'saml_data' not in session:
            session['saml_data'] = {}

        try:
            return f(*args, **kwargs)
        finally:
            # Explicitly tell the session that it has been modified,
            # since just adding/removing an item in the session['saml_data']
            # dict is not picked up as no items in the session dict itself
            # are changed. See:
            # http://flask.pocoo.org/docs/1.0/api/?highlight=session#flask.session
            session.modified = True

    return wrapper


def _requires_active_sign_up_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not sign_up_session_active():
            raise BusinessRuleException('No SAML sign up session active.')

        try:
            return f(*args, **kwargs)
        finally:
            session.modified = True

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
def set_linking_user(user):
    session['saml_data']['linking_user_id'] = user.id


@_requires_saml_data
def is_linking_user_current_user():
    user_id = session['saml_data'].get('linking_user_id')
    return user_id is None or user_id == current_user.id


@_requires_saml_data
def get_linking_user():
    user_id = session['saml_data'].get('linking_user_id')
    if not user_id:
        return current_user

    return user_service.get_user_by_id(user_id)


@_requires_saml_data
def user_is_authenticated():
    return session['saml_data'].get('is_authenticated', False)


@_requires_saml_data
def get_attributes():
    return session['saml_data'].get('attributes', {})


def get_uid_from_attributes():
    attributes = get_attributes()
    return attributes.get('urn:mace:dir:attribute-def:uid')[0]


def get_user_by_uid():
    uid = get_uid_from_attributes()

    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    user = user_service.get_user_by_student_id(uid)

    if user.disabled:
        raise AuthorizationException("User is disabled.")

    return user


def uid_is_linked_to_other_user():
    uid = get_uid_from_attributes()
    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    other_user = user_service.find_user_by_student_id(uid)
    return other_user is not None


def user_is_student():
    attributes = get_attributes()
    affiliation = attributes.get(
        'urn:mace:dir:attribute-def:eduPersonAffiliation')

    if not affiliation:
        return False

    return 'student' in affiliation


def link_uid_to_user(user):
    uid = get_uid_from_attributes()
    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    other_user = user_service.find_user_by_student_id(uid)

    if other_user is not None:
        raise BusinessRuleException("uid already linked to other user.")

    if not user_is_student():
        raise BusinessRuleException("Authenticated user is not a student.")

    user_service.clear_unconfirmed_student_id_in_all_users(uid)
    user_service.set_confirmed_student_id(user, uid)


@_requires_saml_data
def get_nameid():
    return session['saml_data'].get('nameid')


@_requires_saml_data
def clear_saml_data():
    del session['saml_data']


def fill_sign_up_form_with_saml_attributes(form):
    attributes = get_attributes()

    given_name = attributes.get('urn:mace:dir:attribute-def:givenName')
    surname = attributes.get('urn:mace:dir:attribute-def:sn')
    student_id = attributes.get('urn:mace:dir:attribute-def:uid')
    email = attributes.get('urn:mace:dir:attribute-def:mail')
    preferred_language = \
        attributes.get('urn:mace:dir:attribute-def:preferredLanguage')

    if given_name:
        form.first_name.data = given_name[0]
    if surname:
        form.last_name.data = surname[0]
    if student_id:
        form.student_id.data = student_id[0]
    if email:
        form.email.data = email[0]
    if preferred_language and \
            preferred_language[0] in app.config['LANGUAGES'].keys():
        form.locale.data = preferred_language[0]


def start_sign_up_session():
    uid = get_uid_from_attributes()
    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    session['saml_sign_up_session'] = {
        'time_touched': dt.now(),
        'linking_student_id': uid
    }


def sign_up_session_active():
    if 'saml_sign_up_session' in session:
        if dt.now() - session['saml_sign_up_session']['time_touched'] \
                < SIGN_UP_SESSION_TIMEOUT:
            return True

    return False


@_requires_active_sign_up_session
def update_sign_up_session_timestamp():
    session['saml_sign_up_session']['time_touched'] = dt.now()


@_requires_active_sign_up_session
def get_sign_up_session_linking_student_id():
    return session['saml_sign_up_session']['linking_student_id']


@_requires_active_sign_up_session
def end_sign_up_session():
    del session['saml_sign_up_session']
