from flask import Blueprint, url_for, redirect, flash
from flask_login import current_user, login_required
from flask_babel import _

from app.views import get_safe_redirect_url, redirect_back
from app.service import saml_service, user_service
from app.decorators import require_role, response_headers
from app.roles import Roles


blueprint = Blueprint('saml', __name__, url_prefix='/saml')


@blueprint.before_request
def build_saml_info():
    global saml_info
    saml_info = saml_service.build_saml_info()


@blueprint.route('/', methods=['GET'])
def root():
    return redirect(url_for('.login'))


@blueprint.route('/sign-in/', methods=['GET'])
def login():
    redirect_to = get_safe_redirect_url()

    if current_user.is_authenticated:
        return redirect(redirect_to)

    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.sign_in_saml_response')))


@blueprint.route('/sign-up/', methods=['GET'])
def sign_up():
    if current_user.is_authenticated:
        return redirect_back()

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.sign_up_saml_response'), force_authn=True))


@blueprint.route('/link-account/', methods=['GET'])
@login_required
def link_account():
    redirect_to = get_safe_redirect_url()

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
    redirect_to = get_safe_redirect_url()

    user = user_service.get_user_by_id(user_id)
    saml_service.set_linking_user(user)
    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.process_account_linking_saml_response'),
        force_authn=True))


@blueprint.route('/acs/', methods=['POST'])
def assertion_consumer_service():
    saml_service.process_response(saml_info)

    redirect_url = saml_service.get_relaystate_redirect_url(
        saml_info, url_for('home.home'))

    return redirect(redirect_url)


@blueprint.route('/metadata/', methods=['GET'])
@response_headers({'Content-Type': 'application/xml',
                   'Content-Disposition': 'inline; filename="metadata.xml"'})
def metadata():
    return saml_service.build_metadata(saml_info)
