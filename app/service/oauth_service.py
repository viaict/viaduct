import logging
from authlib.specs import rfc6750, rfc7662
from authlib.specs import rfc7009
from authlib.specs.rfc6749 import grants
from flask import url_for
from oauthlib.common import generate_token

from app.exceptions import BusinessRuleException, ResourceNotFoundException, \
    DetailedException
from app.oauth_scopes import Scopes
from app.repository import oauth_repository
from app.service import user_service

_logger = logging.getLogger(__name__)


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):

    def create_authorization_code(self, client, grant_user, request):
        code = generate_token(48)
        oauth_repository.create_authorization_code(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=grant_user.get_user_id()
        )

        return code

    def parse_authorization_code(self, code, client):
        item = oauth_repository.get_authorization_code_by_client_id_and_code(
            client_id=client.client_id, code=code)
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        oauth_repository.delete_authorization_code(authorization_code)

    def authenticate_user(self, authorization_code):
        return user_service.get_user_by_id(authorization_code.user_id)


class RefreshTokenGrant(grants.RefreshTokenGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']

    def authenticate_refresh_token(self, refresh_token: str):
        item = oauth_repository.get_token_by_refresh_token(refresh_token)
        # define is_refresh_token_expired by yourself
        if item and not item.is_refresh_token_expired():
            return item

    def authenticate_user(self, credential):
        return user_service.get_user_by_id(credential.user_id)


class BearerTokenValidator(rfc6750.BearerTokenValidator):
    def authenticate_token(self, token_string):
        return oauth_repository.get_token_by_access_token(token_string)

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return token.revoked


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']

    def authenticate_user(self, email, password):
        try:
            return user_service.get_user_by_login(
                email=email, password=password)
        except DetailedException as e:
            _logger.info("Invalid credentials for password grant.", e)


def _query_token(token, token_type_hint, client):
    if token_type_hint == 'access_token':
        return oauth_repository.get_token_by_access_token(
            access_token=token, client_id=client.client_id)
    elif token_type_hint == 'refresh_token':
        return oauth_repository.get_token_by_refresh_token(
            refresh_token=token, client_id=client.client_id)

    # Without token_type_hint
    item = oauth_repository.get_token_by_access_token(
        access_token=token, client_id=client.client_id)
    if item:
        return item
    return oauth_repository.get_token_by_refresh_token(
        refresh_token=token, client_id=client.client_id)


class RevocationEndpoint(rfc7009.RevocationEndpoint):
    CLIENT_AUTH_METHODS = ['none', 'client_secret_post', 'client_secret_basic']

    def query_token(self, token, token_type_hint, client):
        return _query_token(token, token_type_hint, client)

    def revoke_token(self, token):
        oauth_repository.revoke_token(token)


class IntrospectionEndpoint(rfc7662.IntrospectionEndpoint):
    CLIENT_AUTH_METHODS = ['none', 'client_secret_post', 'client_secret_basic']

    def query_token(self, token, token_type_hint, client):
        return _query_token(token, token_type_hint, client)

    def introspect_token(self, token):
        return {
            'active': True,
            'client_id': token.client_id,
            'token_type': token.token_type,
            'username': token.user.email,
            'scope': token.get_scope(),
            'sub': token.user.id,
            'aud': token.client_id,
            'iss': url_for('home.home', _external=True),
            'exp': token.get_expires_at(),
            'iat': token.issued_at,
        }


def get_client_by_id(client_id):
    return oauth_repository.get_client_by_id(client_id)


def create_token(token, request):
    if request.user:
        user_id = request.user.get_user_id()
    else:
        # client_credentials grant_type
        user_id = request.client.user_id

    client_id = request.client.client_id

    return oauth_repository.create_token(client_id=client_id, user_id=user_id,
                                         **token)


def get_approved_clients_by_user_id(user_id):
    return oauth_repository.get_approved_clients_by_user_id(user_id=user_id)


def user_has_approved_client(user_id, client):
    """Check whether the user has already approved client."""
    return client in oauth_repository.get_approved_clients_by_user_id(user_id)


def get_owned_clients_by_user_id(user_id):
    return oauth_repository.get_owned_clients_by_user_id(user_id=user_id)


def revoke_user_tokens_by_client_id(user_id, client_id):
    client = oauth_repository.get_client_by_id(client_id=client_id)
    if not client:
        raise ResourceNotFoundException("oauth client", client_id)

    oauth_repository.revoke_user_tokens_by_client_id(
        user_id=user_id, client_id=client_id)
    return client


def get_scope_descriptions():
    return {scope.name: scope.value for scope in Scopes}


def create_client(user_id, name, description, redirect_uri_list, scopes):
    raise NotImplementedError()


def update_client(client_id, name, description, redirect_uri_list, scopes):
    raise NotImplementedError()


def reset_client_secret(client_id):
    client = get_client_by_id(client_id)
    if not client:
        raise ResourceNotFoundException("oauth client", client_id)

    if client.client_secret:
        new_client_secret = generate_token(48)
        oauth_repository.update_client_secret(client_id=client_id,
                                              client_secret=new_client_secret)
    else:
        raise BusinessRuleException("public clients have no client_secret.")
