import random
import string
from datetime import timedelta, datetime

from app import ResourceNotFoundException
from app.oauth_scopes import Scopes
from app.repository import oauth_repository as repository


def get_client_by_id(client_id):
    return repository.get_client_by_id(client_id)


def get_grant_by_client_id_and_code(client_id, code):
    return repository.get_grant_by_client_id_and_code(client_id, code)


def create_grant(client_id, code, user_id, request):
    expires = datetime.utcnow() + timedelta(seconds=100)

    return repository.create_grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        scopes=request.scopes,
        user_id=user_id,
        expires=expires)


def get_token(access_token, refresh_token):
    if access_token:
        return repository.get_token_by_access_token(access_token)
    elif refresh_token:
        return repository.get_token_by_refresh_token(refresh_token)


def create_token(token, user_id, request):
    client_id = request.client.client_id
    repository.delete_user_tokens_by_client_id(user_id=user_id,
                                               client_id=client_id)

    expires_in = token.get('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    access_token = token.get('access_token')
    refresh_token = token.get('refresh_token')
    token_type = token['token_type']
    scopes = token['scope'].split()

    return repository.create_token(access_token, refresh_token,
                                   token_type, scopes, expires,
                                   client_id, user_id)


def delete_grant(grant_id):
    repository.delete_grant(grant_id)


def get_approved_clients_by_user_id(user_id):
    return repository.get_approved_clients_by_user_id(user_id=user_id)


def user_has_approved_client(user_id, client):
    """
    Check whether the user has already approved client.
    """
    return client in repository.get_approved_clients_by_user_id(user_id)


def get_owned_clients_by_user_id(user_id):
    return repository.get_owned_clients_by_user_id(user_id=user_id)


def delete_user_tokens_by_client_id(user_id, client_id):
    client = repository.get_client_by_id(client_id=client_id)
    if not client:
        raise ResourceNotFoundException("oauth client", client_id)

    repository.delete_user_tokens_by_client_id(
        user_id=user_id, client_id=client_id)
    return client


def delete_token(token_id):
    repository.delete_token(token_id=token_id)


def get_scope_descriptions():
    return {scope.name: scope.value for scope in Scopes}


def generate_random_str(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(length))


def generate_client_id():
    client_id = generate_random_str(20)
    while repository.get_client_by_id(client_id=client_id):
        client_id = generate_random_str(20)
    return client_id


def generate_client_secret():
    client_secret = generate_random_str(40)
    while repository.get_client_by_secret(client_secret=client_secret):
        client_secret = generate_random_str(40)
    return client_secret


def split_redirect_uris(redirect_uri_list):
    return list(filter(lambda x: x,
                       [uri.strip() for uri in redirect_uri_list.split(",")]))


def create_client(user_id, name, description, redirect_uri_list, scopes):
    client_id = generate_client_id()
    client_secret = generate_client_secret()

    redirect_uris = split_redirect_uris(redirect_uri_list)
    scopes = [scope.name for scope in scopes]

    client = repository.create_client(
        client_id=client_id,
        client_secret=client_secret,
        name=name,
        description=description,
        redirect_uris=redirect_uris,
        user_id=user_id,
        confidential=False,
        default_scopes=scopes)

    return client


def update_client(client_id, name, description, redirect_uri_list, scopes):
    repository.update_client_details(
        client_id=client_id, name=name, description=description)

    current_uris = set(repository.get_redirect_uris_by_client_id(
        client_id=client_id))
    new_uris = set(split_redirect_uris(redirect_uri_list))

    removed_uris = current_uris - new_uris
    added_uris = new_uris - current_uris
    if removed_uris:
        repository.delete_redirect_uris(client_id=client_id,
                                        redirect_uri_list=removed_uris)
    if added_uris:
        repository.insert_redirect_uris(client_id=client_id,
                                        redirect_uri_list=added_uris)

    current_scopes = set(repository.get_scopes_by_client_id(
        client_id=client_id))
    new_scopes = set(scope for scope in scopes)
    removed_scopes = current_scopes - new_scopes
    added_scopes = new_scopes - current_scopes

    if removed_scopes:
        repository.delete_scopes(client_id=client_id,
                                 scopes_list=removed_scopes)
    if added_scopes:
        repository.insert_scopes(client_id=client_id,
                                 scopes_list=added_scopes)


def reset_client_secret(client_id):
    new_client_secret = generate_client_secret()
    repository.update_client_secret(client_id=client_id,
                                    client_secret=new_client_secret)
