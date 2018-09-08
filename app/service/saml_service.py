from collections import namedtuple

from datetime import datetime as dt, timedelta
from flask import session, request
from flask_login import current_user
from functools import wraps
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from urllib.parse import urlparse

from app import app, constants
from app.exceptions.base import ValidationException, AuthorizationException, \
    BusinessRuleException
from app.service import user_service

SAMLInfo = namedtuple('SAMLInfo', ['auth', 'req'])

# Session keys

SESSION_SAML_DATA = 'saml_data'
SESSION_SAML_SIGN_UP_SESSION = 'saml_sign_up_session'

# SAML data dict keys

SAML_DATA_IS_AUTHENTICATED = 'is_authenticated'
SAML_DATA_ATTRIBUTES = 'attributes'
SAML_DATA_NAMEID = 'nameid'
SAML_DATA_REDIRECT_URL = 'redirect_url'
SAML_DATA_LINKING_USER_ID = 'linking_user_id'

# SAML sign up session dict keys and timeout

SIGN_UP_SESSION_TIME_TOUCHED = 'time_touched'
SIGN_UP_SESSION_LINKING_STUDENT_ID = 'linking_student_id'
SIGN_UP_SESSION_TIMEOUT = timedelta(minutes=5)

# SAML attribute URNs.
# See this wiki page for a more detailed description of the attributes:
# https://wiki.surfnet.nl/display/surfconextdev/Attributes

# Examples: '12345678' (in case of a student), 'jdoe1' (in case of an employee)
ATTR_URN_UID = 'urn:mace:dir:attribute-def:uid'

# Example: ['student', 'member', 'affiliate']
ATTR_URN_PERSON_AFFILIATION = 'urn:mace:dir:attribute-def:eduPersonAffiliation'

# Examples: 'John', 'John Davison'
ATTR_URN_GIVEN_NAME = 'urn:mace:dir:attribute-def:givenName'

# Example: 'Doe', 'van der Sanden'
ATTR_URN_SURNAME = 'urn:mace:dir:attribute-def:sn'

# Examples: 'john.doe@student.uva.nl', 'j.d.doe@uva.nl'
ATTR_URN_MAIL = 'urn:mace:dir:attribute-def:mail'

# Examples: 'nl', 'en'
ATTR_URN_PREFERRED_LANGUAGE = 'urn:mace:dir:attribute-def:preferredLanguage'


def _requires_saml_data(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if SESSION_SAML_DATA not in session:
            session[SESSION_SAML_DATA] = {}

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
            raise ValidationException('No SAML sign up session active.')

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

    # This is the base path for all SAML config files and certificates
    # It is equal to "saml/{develop,master}" and is structured as follows:
    # saml/{develop,master}/
    #   settings.json:              General settings
    #   advanced_settings.json:     Some extra settings
    #   certs/sp.{key,crt}          Certificate and private key

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
        session[SESSION_SAML_DATA][SAML_DATA_IS_AUTHENTICATED] = True
        session[SESSION_SAML_DATA][SAML_DATA_ATTRIBUTES] = \
            saml_auth.get_attributes()
        session[SESSION_SAML_DATA][SAML_DATA_NAMEID] = saml_auth.get_nameid()
    else:
        session[SESSION_SAML_DATA][SAML_DATA_IS_AUTHENTICATED] = False


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
        return metadata
    else:
        raise ValidationException(
            'Errors occurred when building SAML metadata: {}'.format(
                ', '.join(errors)))


@_requires_saml_data
def set_redirect_url(redirect_url):
    session[SESSION_SAML_DATA][SAML_DATA_REDIRECT_URL] = redirect_url


@_requires_saml_data
def get_redirect_url(fallback_url):
    return session[SESSION_SAML_DATA].get(SAML_DATA_REDIRECT_URL, fallback_url)


@_requires_saml_data
def set_linking_user(user):
    session[SESSION_SAML_DATA][SAML_DATA_LINKING_USER_ID] = user.id


@_requires_saml_data
def is_linking_user_current_user():
    user_id = session[SESSION_SAML_DATA].get(SAML_DATA_LINKING_USER_ID)
    return user_id is None or user_id == current_user.id


@_requires_saml_data
def get_linking_user():
    user_id = session[SESSION_SAML_DATA].get(SAML_DATA_LINKING_USER_ID)
    if not user_id:
        return current_user

    return user_service.get_user_by_id(user_id)


@_requires_saml_data
def user_is_authenticated():
    return session[SESSION_SAML_DATA].get(SAML_DATA_IS_AUTHENTICATED, False)


@_requires_saml_data
def get_attributes():
    return session[SESSION_SAML_DATA].get(SAML_DATA_ATTRIBUTES, {})


def get_uid_from_attributes():
    attributes = get_attributes()

    value = attributes.get(ATTR_URN_UID)
    if not value:
        return None

    # Since attributes are always lists, we use [0] to
    # pick the first and only value.
    return value[0]


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
    affiliation = attributes.get(ATTR_URN_PERSON_AFFILIATION)

    if not affiliation:
        return False

    return 'student' in affiliation


def link_uid_to_user(user):
    uid = get_uid_from_attributes()
    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    if not user_is_student():
        raise BusinessRuleException("Authenticated user is not a student.")

    user_service.set_confirmed_student_id(user, uid)


@_requires_saml_data
def get_nameid():
    return session[SESSION_SAML_DATA].get(SAML_DATA_NAMEID)


@_requires_saml_data
def clear_saml_data():
    del session[SESSION_SAML_DATA]


def fill_sign_up_form_with_saml_attributes(form):
    attributes = get_attributes()

    given_name = attributes.get(ATTR_URN_GIVEN_NAME)
    surname = attributes.get(ATTR_URN_SURNAME)
    student_id = attributes.get(ATTR_URN_UID)
    email = attributes.get(ATTR_URN_MAIL)
    preferred_language = attributes.get(ATTR_URN_PREFERRED_LANGUAGE)

    # Check which attributes are present and fill the form
    # with their data. Since attributes are always lists, we use [0] to
    # pick the first and only value of each attribute.

    if given_name:
        form.first_name.data = given_name[0]
    if surname:
        form.last_name.data = surname[0]
    if student_id:
        form.student_id.data = student_id[0]
    if email:
        form.email.data = email[0]
    if preferred_language and \
            preferred_language[0] in constants.LANGUAGES.keys():
        form.locale.data = preferred_language[0]


def start_sign_up_session():
    uid = get_uid_from_attributes()
    if not uid:
        raise ValidationException('uid not found in SAML attributes')

    session[SESSION_SAML_SIGN_UP_SESSION] = {
        SIGN_UP_SESSION_TIME_TOUCHED: dt.now(),
        SIGN_UP_SESSION_LINKING_STUDENT_ID: uid
    }


def sign_up_session_active():
    if SESSION_SAML_SIGN_UP_SESSION in session:
        if dt.now() - session[SESSION_SAML_SIGN_UP_SESSION][
            SIGN_UP_SESSION_TIME_TOUCHED] < SIGN_UP_SESSION_TIMEOUT:
            return True

    return False


@_requires_active_sign_up_session
def update_sign_up_session_timestamp():
    session[SESSION_SAML_SIGN_UP_SESSION][SIGN_UP_SESSION_TIME_TOUCHED] = \
        dt.now()


@_requires_active_sign_up_session
def get_sign_up_session_linking_student_id():
    # Using [...] instead of .get(...) here as this raises a KeyError
    # when linking_student_id is not present, which means that
    # the sign up session was not initialised correctly.
    return session[SESSION_SAML_SIGN_UP_SESSION][
        SIGN_UP_SESSION_LINKING_STUDENT_ID]


@_requires_active_sign_up_session
def end_sign_up_session():
    del session[SESSION_SAML_SIGN_UP_SESSION]
