from flask import request, Blueprint, render_template
from flask_login import login_required, current_user

from app import oauth, version
from app.service import oauth_service

blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')


@blueprint.route('/authorize/', methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = oauth_service.get_client_by_id(client_id=client_id)
        kwargs['client'] = client
        kwargs['user'] = current_user
        return render_template('oauth/oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@blueprint.route('/token/', methods=['POST'])
@oauth.token_handler
def access_token():
    return {'version': version}


@blueprint.route('/revoke/', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    pass
