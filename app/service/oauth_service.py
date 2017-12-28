import random
import string
from datetime import timedelta, datetime

from app import ResourceNotFoundException
from app.oauth_scopes import Scopes
from app.repository import oauth_repository


def get_client_by_id(client_id):
    return oauth_repository.get_client_by_id(client_id)


def get_grant_by_client_id_and_code(client_id, code):
    return oauth_repository.get_grant_by_client_id_and_code(client_id, code)


def create_grant(client_id, code, user_id, request):
    expires = datetime.utcnow() + timedelta(seconds=100)

    return oauth_repository.create_grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        scopes=request.scopes,
        user_id=user_id,
        expires=expires)


def get_token(access_token, refresh_token):
    if access_token:
        return oauth_repository.get_token_by_access_token(access_token)
    elif refresh_token:
        return oauth_repository.get_token_by_refresh_token(refresh_token)


def create_token(token, user_id, request):
    client_id = request.client.client_id
    oauth_repository.delete_user_tokens_by_client_id(user_id=user_id,
                                                     client_id=client_id)

    expires_in = token.get('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    access_token = token.get('access_token')
    refresh_token = token.get('refresh_token')
    token_type = token['token_type']
    scopes = token['scope'].split()

    return oauth_repository.create_token(access_token, refresh_token,
                                         token_type, scopes, expires,
                                         client_id, user_id)


def delete_grant(grant_id):
    oauth_repository.delete_grant(grant_id)


def get_approved_clients_by_user_id(user_id):
    return oauth_repository.get_approved_clients_by_user_id(user_id=user_id)


def get_owned_clients_by_user_id(user_id):
    return oauth_repository.get_owned_clients_by_user_id(user_id=user_id)


def delete_user_tokens_by_client_id(user_id, client_id):
    client = oauth_repository.get_client_by_id(client_id=client_id)
    if not client:
        raise ResourceNotFoundException("oauth client", client_id)

    oauth_repository.delete_user_tokens_by_client_id(
        user_id=user_id, client_id=client_id)
    return client


def delete_token(token_id):
    oauth_repository.delete_token(token_id=token_id)


def get_all_scopes():
    return [scope.name for scope in Scopes]


def get_scope_descriptions():
    return {scope.name: scope.value for scope in Scopes}


def generate_random_str(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(length))


def generate_client_id():
    client_id = generate_random_str(20)
    while oauth_repository.get_client_by_id(client_id=client_id):
        client_id = generate_random_str(20)
    return client_id


def generate_client_secret():
    client_secret = generate_random_str(40)
    while oauth_repository.get_client_by_secret(client_secret=client_secret):
        client_secret = generate_random_str(40)
    return client_secret


def create_client(user_id, name, description, redirect_uri):
    client_id = generate_client_id()
    client_secret = generate_client_secret()

    scopes = get_all_scopes()

    client = oauth_repository.create_client(
        client_id=client_id,
        client_secret=client_secret,
        name=name,
        description=description,
        redirect_uri=redirect_uri,
        user_id=user_id,
        confidential=False,
        default_scopes=scopes)

    return client


def update_client(client_id, name, description, redirect_uri):
    oauth_repository.update_client_details(
        client_id=client_id, name=name, description=description)
    oauth_repository.update_client_redirect_uri(client_id=client_id,
                                                redirect_uri=redirect_uri)


def reset_client_secret(client_id):
    new_client_secret = generate_client_secret()
    oauth_repository.update_client_secret(client_id=client_id,
                                          client_secret=new_client_secret)
