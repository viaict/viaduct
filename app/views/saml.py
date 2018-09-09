import re
from flask import Blueprint, url_for, redirect, flash, session, request
from flask_babel import _
from flask_login import current_user, login_required

from app.decorators import require_role, response_headers
from app.exceptions.base import ValidationException
from app.roles import Roles
from app.service import saml_service, user_service
from app.views import get_safe_redirect_url, redirect_back

blueprint = Blueprint('saml', __name__, url_prefix='/saml')


def get_redirect_url():
    # If referer is empty for some reason (browser policy, user entered
    # address in address bar, etc.), use empty string
    referer = request.headers.get('Referer', '')

    denied = (re.match(r'(?:https?://[^/]+)%s$' % (url_for('user.sign_in')),
                       referer) is not None)
    denied_from = session.get('denied_from')

    if denied and denied_from:
        return denied_from

    return get_safe_redirect_url()


@blueprint.before_request
def build_saml_info():
    global saml_info
    saml_info = saml_service.build_saml_info()


@blueprint.route('/', methods=['GET'])
def root():
    return redirect(url_for('.login'))


@blueprint.route('/sign-in/', methods=['GET'])
def login():
    """Initiate a login with SURFconext."""
    redirect_to = get_redirect_url()

    if current_user.is_authenticated:
        return redirect(redirect_to)

    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.sign_in_saml_response')))


@blueprint.route('/sign-up/', methods=['GET'])
def sign_up():
    """
    Initiate a sign-up session with SURFconext.

    Initiate a sign-up session by first letting the user log in via SURFconext
    to partially pre-fill the sign-up form.
    """

    if current_user.is_authenticated:
        return redirect_back()

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.sign_up_saml_response'), force_authn=True))


@blueprint.route('/link-account/', methods=['GET'])
@login_required
def link_account():
    """
    Let a user link his/her account.

    Let the currently logged in user log in in SURFconext to
    link his/her via account to his UvA account.
    """

    redirect_to = get_redirect_url()

    if current_user.student_id_confirmed:
        flash(_('Your account is already linked to a UvA account.'), 'danger')
        return redirect(redirect_to)

    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.process_account_linking_saml_response'),
        force_authn=True))


@blueprint.route('/link-account/<int:user_id>/', methods=['GET'])
@login_required
@require_role(Roles.USER_WRITE)
def link_other_account(user_id):
    """
    Link the account of another user.

    Let a user log in via SURFconext to link that UvA account to the via
    account with id user_id.
    """

    redirect_to = get_redirect_url()

    user = user_service.get_user_by_id(user_id)
    saml_service.set_linking_user(user)
    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.process_account_linking_saml_response'),
        force_authn=True))


@blueprint.route('/acs/', methods=['POST'])
def assertion_consumer_service():
    """
    The Assertion Consumer Service endpoint for SAML IDP responses.

    This endpoint receives and processes the SAML response from SURFconext
    and then redirects to the handler set by initiate_login
    (which saves it in the RelayState parameter of the SAML request).
    """

    try:
        saml_service.process_response(saml_info)
    except ValidationException:
        flash(_('The response from SURFconext was invalid.'), 'danger')

        return redirect(saml_service.get_redirect_url(url_for('home.home')))

    redirect_url = saml_service.get_relaystate_redirect_url(
        saml_info, url_for('home.home'))

    return redirect(redirect_url)


@blueprint.route('/metadata/', methods=['GET'])
@response_headers({'Content-Type': 'application/xml',
                   'Content-Disposition': 'inline; filename="metadata.xml"'})
def metadata():
    """Build the metadata XML and output it."""

    return saml_service.build_metadata(saml_info)
