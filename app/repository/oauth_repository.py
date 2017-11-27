from app import db
from app.models.oauth.client import OAuthClient
from app.models.oauth.grant import OAuthGrant
from app.models.oauth.token import OAuthToken


def get_client_by_id(client_id):
    return db.session.query(OAuthClient) \
        .filter_by(client_id=client_id) \
        .one_or_none()


def get_grant_by_client_id_and_code(client_id, code):
    return db.session.query(OAuthGrant) \
        .filter_by(client_id=client_id, code=code) \
        .one_or_none()


def create_grant(client_id, code, redirect_uri, scopes, user_id, expires):
    grant = OAuthGrant(client_id=client_id, code=code,
                       redirect_uri=redirect_uri,
                       _scopes=scopes, user_id=user_id, expires=expires)
    db.session.add(grant)
    db.session.commit()
    return grant


def get_token_by_access_token(access_token):
    return db.session.query(OAuthToken) \
        .filter_by(access_token=access_token) \
        .one_or_none()


def get_token_by_refresh_token(refresh_token):
    return db.session.query(OAuthToken) \
        .filter_by(refresh_token=refresh_token) \
        .one_or_none()


def remove_tokens_for_client_user(client_id, user_id):
    db.session.query(OAuthToken).filter_by(
        client_id=client_id,
        user_id=user_id
    ).delete(synchronize_session='fetch')
    db.session.commit()


def create_token(access_token, refresh_token, token_type, scopes, expires,
                 client_id, user_id):
    tok = OAuthToken(access_token=access_token, refresh_token=refresh_token,
                     token_type=token_type, _scopes=scopes, expires=expires,
                     client_id=client_id, user_id=user_id)
    db.session.add(tok)
    db.session.commit()
    return tok


def delete_grant(grant_id):
    db.session.query(OAuthGrant).filter_by(
        id=grant_id
    ).delete(synchronize_session='fetch')
    db.session.commit()
