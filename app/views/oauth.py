from flask import request, Blueprint, render_template, url_for, redirect, \
    flash, jsonify
from flask_babel import _
from flask_login import login_required, current_user

from app import oauth, version
from app.decorators import response_headers
from app.forms.oauth_forms import OAuthClientForm
from app.oauth_scopes import Scopes
from app.service import oauth_service

blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')


@blueprint.route('/authorize/', methods=['GET', 'POST'])
@login_required
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
@oauth.authorize_handler
def authorize(*__, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = oauth_service.get_client_by_id(client_id=client_id)
        kwargs['client'] = client
        kwargs['user'] = current_user
        kwargs['descriptions'] = oauth_service.get_scope_descriptions()
        return render_template('oauth/oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == _("Confirm")


@blueprint.route('/token/', methods=['GET', 'POST'])
@oauth.token_handler
def access_token():
    return {'version': version}


@blueprint.route('/revoke/', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    pass


@blueprint.route("/token/info/")
@oauth.require_oauth()
def token_info():
    return jsonify({"active": "true",
                    "scope": request.oauth.access_token.scopes,
                    "username": request.oauth.user.email,
                    "expires": request.oauth.access_token.expires,
                    "client_id": request.oauth.client.client_id,
                    "first_name": request.oauth.user.first_name,
                    "last_name": request.oauth.user.last_name
                    })


@oauth.invalid_response
def invalid_token_info(request):
    return jsonify({"active": "false"})


@blueprint.route("/errors/", methods=['GET'])
def errors():
    error = request.args.get("error", _("Unknown OAuth error"))
    error_description = request.args.get("error_description",
                                         _("Please try again"))
    return render_template('oauth/error.htm',
                           error=error, description=error_description)


@blueprint.route("/clients/", methods=["GET"])
@login_required
def list_clients():
    owned_clients = oauth_service.get_owned_clients_by_user_id(
        user_id=current_user.id)
    clients = oauth_service.get_approved_clients_by_user_id(
        user_id=current_user.id)
    return render_template('oauth/list_client.htm',
                           owned_clients=owned_clients,
                           clients=clients)


@blueprint.route("/clients/revoke/<string:client_id>/", methods=['POST'])
def revoke_client_token(client_id=None):
    client = oauth_service.delete_user_tokens_by_client_id(
        user_id=current_user.id, client_id=client_id)
    flash(_("Successfully revoked token for client '%s'" % client.name))
    return redirect(url_for("oauth.list_clients"))


@blueprint.route("/clients/reset/<string:client_id>/", methods=["POST"])
def reset_client_secret(client_id):
    oauth_service.reset_client_secret(client_id)
    return redirect(url_for("oauth.list_clients"))


@blueprint.route("/clients/register/", methods=["GET", "POST"])
@blueprint.route("/clients/edit/<string:client_id>/", methods=["GET", "POST"])
def edit(client_id=None):
    client = oauth_service.get_client_by_id(client_id=client_id)
    form = OAuthClientForm(request.form, obj=client)

    if form.redirect_uri.data is None and client:
        form.redirect_uri.data = ', '.join(client.redirect_uris)
    if form.scopes.data is None and client:
        form.scopes.data = [Scopes[s] for s in client.default_scopes]

    if form.validate_on_submit():
        if client:
            oauth_service.update_client(
                client_id=client_id, name=form.name.data,
                description=form.description.data,
                redirect_uri_list=form.redirect_uri.data,
                scopes=form.scopes.data)
            flash(_("Successfully updated client '%s'" % client.name))
        else:
            client = oauth_service.create_client(
                user_id=current_user.id,
                name=form.name.data,
                description=form.description.data,
                redirect_uri_list=form.redirect_uri.data,
                scopes=form.scopes.data)
            flash(_("Successfully created client '%s'" % client.name))
        return redirect(url_for("oauth.list_clients"))
    return render_template("oauth/register.htm", form=form)
