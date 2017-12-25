from datetime import timedelta, datetime

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
    oauth_repository.remove_tokens_for_client_user(client_id, user_id)

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
