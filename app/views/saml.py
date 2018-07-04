from flask import Blueprint, url_for, redirect, request, flash
from flask_login import current_user, login_required
from flask_babel import _

from app.service import saml_service, user_service
from app.decorators import require_role
from app.roles import Roles

from functools import wraps


blueprint = Blueprint('saml', __name__, url_prefix='/saml')


def saml_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        global saml_info
        saml_info = saml_service.build_saml_info()

        return f(*args, **kwargs)

    return wrapper


@blueprint.route('/', methods=['GET'])
def root():
    return redirect(url_for('.login'))


@blueprint.route('/sign-in/', methods=['GET'])
@saml_route
def login():
    redirect_to = request.headers.get('Referer', url_for('home.home'))

    if current_user.is_authenticated:
        return redirect(redirect_to)

    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.sign_in_saml_response')))


@blueprint.route('/sign-up/', methods=['GET'])
@saml_route
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.sign_up_saml_response'), force_authn=True))


@blueprint.route('/link-account/', methods=['GET'])
@login_required
@saml_route
def link_account():
    redirect_to = request.headers.get('Referer', url_for('home.home'))

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
@saml_route
def link_other_account(user_id):
    redirect_to = request.headers.get('Referer', url_for('home.home'))

    user = user_service.get_user_by_id(user_id)
    saml_service.set_linking_user(user)
    saml_service.set_redirect_url(redirect_to)

    return redirect(saml_service.initiate_login(
        saml_info, url_for('user.process_account_linking_saml_response'),
        force_authn=True))


@blueprint.route('/acs/', methods=['POST'])
@saml_route
def assertion_consumer_service():
    saml_service.process_response(saml_info)

    redirect_url = saml_service.get_relaystate_redirect_url(
        saml_info, url_for('home.home'))

    return redirect(redirect_url)


@blueprint.route('/metadata/', methods=['GET'])
@saml_route
def metadata():
    return saml_service.build_metadata(saml_info)
