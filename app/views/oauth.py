from authlib.specs.rfc6749 import OAuth2Error
from flask import request, Blueprint, render_template, url_for, redirect, \
    flash, abort
from flask_babel import _
from flask_login import login_required, current_user

from app import oauth_server
from app.decorators import response_headers
from app.exceptions.base import BusinessRuleException
from app.forms import init_form
from app.forms.oauth_forms import OAuthClientForm
from app.oauth_scopes import Scopes
from app.service import oauth_service

blueprint = Blueprint('oauth', __name__, url_prefix='/oauth')


@blueprint.route('/authorize', methods=['GET', 'POST'], strict_slashes=False)
@login_required
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def authorize():
    if request.method == 'GET':
        try:
            grant = oauth_server.validate_consent_request(
                end_user=current_user)
        except OAuth2Error as error:
            flash(_("OAuth authorize request was invalid. ") +
                  error.get_error_description(), 'danger')
            return redirect(url_for("home.home"))

        if grant.client.auto_approve:
            return oauth_server.create_authorization_response(current_user)

        if oauth_service.user_has_approved_client(
                user_id=current_user.id, client=grant.client):
            return oauth_server.create_authorization_response(current_user)

        kwargs = {'grant': grant,
                  'user': current_user,
                  'scopes': oauth_service.get_scope_descriptions()}
        return render_template('oauth/oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', False)
    if confirm:
        # granted by resource owner
        return oauth_server.create_authorization_response(current_user)
    # denied by resource owner
    return oauth_server.create_authorization_response(None)


@blueprint.route('/token', methods=['POST'], strict_slashes=True)
def issue_token():
    return oauth_server.create_token_response()


@blueprint.route('/revoke', methods=['POST'], strict_slashes=True)
def revoke_token():
    return oauth_server.create_endpoint_response(
        oauth_service.RevocationEndpoint.ENDPOINT_NAME)


@blueprint.route('/introspect', methods=['POST'], strict_slashes=True)
def introspect_token():
    return oauth_server.create_endpoint_response(
        oauth_service.IntrospectionEndpoint.ENDPOINT_NAME)


@blueprint.route("/errors", methods=['GET'])
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
    approved_clients = oauth_service.get_approved_clients_by_user_id(
        user_id=current_user.id)
    return render_template('oauth/list_client.htm',
                           owned_clients=owned_clients,
                           approved_clients=approved_clients)


@blueprint.route("/clients/revoke/<string:client_id>/", methods=['POST'])
def revoke_client_token(client_id=None):
    client = oauth_service.revoke_user_tokens_by_client_id(
        user_id=current_user.id, client_id=client_id)
    flash(_("Successfully revoked token for client '%s'" % client.client_name))
    return redirect(url_for("oauth.list_clients"))


@blueprint.route("/clients/reset/<string:client_id>/", methods=["POST"])
def reset_client_secret(client_id):
    try:
        oauth_service.reset_client_secret(client_id)
    except BusinessRuleException:
        flash(_("Public clients have no secret."), 'danger')
    return redirect(url_for("oauth.list_clients"))


@blueprint.route("/clients/register/", methods=["GET", "POST"])
@blueprint.route("/clients/edit/<string:client_id>/", methods=["GET", "POST"])
def edit(client_id=None):
    # This is temporary until we allow dynamic client registration.
    abort(404)

    client = oauth_service.get_client_by_id(client_id=client_id)
    form = init_form(OAuthClientForm, obj=client)

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
