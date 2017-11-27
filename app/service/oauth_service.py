from datetime import timedelta, datetime

from flask_login import current_user

from app import oauth
from app.repository import oauth_repository


@oauth.clientgetter
def oauth_clientgetter(client_id):
    return get_client_by_id(client_id)


@oauth.grantgetter
def oauth_grantgetter(client_id, code):
    return get_grant_by_client_id_and_code(client_id, code)


@oauth.grantsetter
def oauth_grantsetter(client_id, code, request, *_, **__):
    return create_grant(client_id, code, request)


@oauth.tokengetter
def oauth_tokengetter(access_token=None, refresh_token=None):
    return get_token(access_token, refresh_token)


@oauth.tokensetter
def oauth_tokensetter(token, request, *_, **__):
    return create_token(token, request)


def get_client_by_id(client_id):
    return oauth_repository.get_client_by_id(client_id)


def get_grant_by_client_id_and_code(client_id, code):
    return oauth_repository.get_grant_by_client_id_and_code(client_id, code)


def create_grant(client_id, code, request):
    expires = datetime.utcnow() + timedelta(seconds=100)
    scopes = ' '.join(request.scopes)
    redirect_uri = request.redirect_uri
    code = code['code']

    return oauth_repository.create_grant(
        client_id=client_id,
        code=code,
        redirect_uri=redirect_uri,
        scopes=scopes,
        user=current_user,
        expires=expires)


def get_token(access_token, refresh_token):
    if access_token:
        return oauth_repository.get_token_by_access_token(access_token)
    elif refresh_token:
        return oauth_repository.get_token_by_refresh_token(refresh_token)


def create_token(token, request):
    client_id = request.client.client_id
    if request.user:
        user_id = request.user.id
    else:
        user_id = current_user.id

    oauth_repository.remove_tokens_for_client_user(client_id, user_id)

    expires_in = token.get('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    access_token = token.get('access_token')
    refresh_token = token.get('refresh_token')
    token_type = token['token_type']
    scopes = token['scope']

    return oauth_repository.create_token(access_token, refresh_token,
                                         token_type, scopes, expires,
                                         client_id, user_id)


def client_default_scope_list(client):
    return client.default_scopes.split() if client.default_scopes else []


def client_redirect_uri_list(client):
    return client.redirect_uris.split() if client.redirect_uris else []


def grant_scope_list(grant):
    return grant.scopes.split() if grant.scopes else []


def token_scope_list(token):
    return token.scopes.split() if token.scopes else []


def delete_grant(grant_id):
    oauth_repository.delete_grant(grant_id)
