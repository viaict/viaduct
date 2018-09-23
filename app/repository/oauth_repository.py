from sqlalchemy.orm import raiseload, joinedload
from typing import Optional

from app import db
from app.models.oauth.client import OAuthClient
from app.models.oauth.code import OAuthAuthorizationCode
from app.models.oauth.token import OAuthToken
from app.models.user import User


def get_client_by_id(client_id):
    return db.session.query(OAuthClient) \
        .filter_by(client_id=client_id) \
        .one_or_none()


def create_token(client_id: str, user_id: int, **token) -> OAuthToken:
    token = OAuthToken(client_id=client_id, user_id=user_id, **token)
    db.session.add(token)
    db.session.commit()
    return token


def get_authorization_code_by_client_id_and_code(client_id, code):
    return db.session.query(OAuthAuthorizationCode) \
        .filter_by(client_id=client_id, code=code) \
        .one_or_none()


def create_authorization_code(code, client_id, redirect_uri, scope, user_id):
    auth_code = OAuthAuthorizationCode(
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        user_id=user_id)
    db.session.add(auth_code)
    db.session.commit()


def get_token_by_user_id(user_id: int, client_id: str) -> Optional[OAuthToken]:
    return db.session.query(OAuthToken) \
        .filter_by(client_id=client_id, user_id=user_id) \
        .order_by(OAuthToken.id.desc()) \
        .first()


def get_token_by_access_token(access_token: str, client_id: str = None) \
        -> Optional[OAuthToken]:
    q = db.session.query(OAuthToken) \
        .filter_by(access_token=access_token)
    if client_id:
        q = q.filter_by(client_id=client_id)
    return q.one_or_none()


def get_token_by_refresh_token(refresh_token: str, client_id: str = None) \
        -> Optional[OAuthToken]:
    q = db.session.query(OAuthToken) \
        .filter_by(refresh_token=refresh_token)
    if client_id:
        q = q.filter_by(client_id=client_id)
    return q.one_or_none()


def delete_authorization_code(authorization_code):
    db.session.delete(authorization_code)
    db.session.commit()


def delete_token(token_id):
    db.session.query(OAuthToken).filter_by(
        id=token_id
    ).delete(synchronize_session=False)
    db.session.commit()


def get_approved_clients_by_user_id(user_id):
    return db.session.query(OAuthClient) \
        .join(OAuthToken, OAuthToken.client_id == OAuthClient.client_id) \
        .filter(OAuthToken.user_id == user_id,
                OAuthToken.revoked == False) \
        .order_by(OAuthClient.client_name) \
        .options(joinedload(OAuthClient.user)
                 .load_only(User.first_name, User.last_name),
                 raiseload("*")) \
        .all()  # noqa


def get_owned_clients_by_user_id(user_id):
    return db.session.query(OAuthClient) \
        .order_by(OAuthClient.client_name) \
        .filter_by(user_id=user_id, auto_approve=False).all()


def revoke_user_tokens_by_client_id(user_id, client_id):
    db.session.query(OAuthToken).filter_by(
        user_id=user_id, client_id=client_id
    ).update(dict(revoked=True))
    db.session.commit()


def revoke_user_tokens_by_user_id(user_id: int):
    db.session.query(OAuthToken).filter_by(
        user_id=user_id
    ).update(dict(revoked=True))
    db.session.commit()


def update_client_secret(client_id, client_secret):
    db.session.query(OAuthClient) \
        .filter_by(client_id=client_id) \
        .update(dict(client_secret=client_secret))
    db.session.commit()


def revoke_token(token):
    token.revoked = True
    db.session.add(token)
    db.session.commit()
