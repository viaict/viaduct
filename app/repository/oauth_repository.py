from sqlalchemy.orm import raiseload, joinedload

from app import db
from app.models.oauth.client import OAuthClient, OAuthClientScope, \
    OAuthClientRedirect
from app.models.oauth.grant import OAuthGrant, OAuthGrantScope
from app.models.oauth.token import OAuthToken, OAuthTokenScope
from app.models.user import User
from app.oauth_scopes import Scopes


def get_client_by_id(client_id):
    return db.session.query(OAuthClient) \
        .filter_by(client_id=client_id) \
        .one_or_none()


def get_client_by_secret(client_secret):
    return db.session.query(OAuthClient) \
        .filter_by(client_secret=client_secret) \
        .one_or_none()


def get_grant_by_client_id_and_code(client_id, code):
    return db.session.query(OAuthGrant) \
        .filter_by(client_id=client_id, code=code) \
        .one_or_none()


def create_grant(client_id, code, redirect_uri, scopes, user_id, expires):
    grants = [OAuthGrantScope(scope=scope) for scope in scopes]
    grant = OAuthGrant(client_id=client_id, code=code,
                       redirect_uri=redirect_uri,
                       user_id=user_id, expires=expires)
    db.session.add_all(grants)
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


def create_token(access_token, refresh_token, token_type, scopes, expires,
                 client_id, user_id):
    new_scopes = [OAuthTokenScope(scope=scope) for scope in scopes]
    tok = OAuthToken(access_token=access_token, refresh_token=refresh_token,
                     token_type=token_type, _scopes=new_scopes,
                     expires=expires, client_id=client_id, user_id=user_id)
    db.session.add_all(new_scopes)
    db.session.add(tok)
    db.session.commit()

    return tok


def delete_grant(grant_id):
    db.session.query(OAuthGrant).filter_by(
        id=grant_id
    ).delete(synchronize_session=False)
    db.session.commit()


def delete_token(token_id):
    db.session.query(OAuthToken).filter_by(
        id=token_id
    ).delete(synchronize_session=False)
    db.session.commit()


def get_approved_clients_by_user_id(user_id):
    return db.session.query(OAuthClient) \
        .join(OAuthToken).filter_by(user_id=user_id) \
        .order_by(OAuthClient.name) \
        .options(joinedload(OAuthClient.user)
                 .load_only(User.first_name, User.last_name),
                 raiseload("*")) \
        .all()


def get_owned_clients_by_user_id(user_id):
    return db.session.query(OAuthClient) \
        .order_by(OAuthClient.name) \
        .filter_by(user_id=user_id, auto_approve=False).all()


def delete_user_tokens_by_client_id(user_id, client_id):
    db.session.query(OAuthToken).filter_by(
        user_id=user_id, client_id=client_id
    ).delete(synchronize_session=False)
    db.session.commit()


def create_client(client_id, client_secret, name, description, redirect_uris,
                  user_id, confidential, default_scopes):
    scopes = [OAuthClientScope(scope=scope) for scope in default_scopes]
    redirect_uris = [OAuthClientRedirect(redirect_uri=redirect_uri)
                     for redirect_uri in redirect_uris]

    client = OAuthClient(client_id=client_id, client_secret=client_secret,
                         user_id=user_id, name=name, description=description,
                         confidential=confidential, _default_scopes=scopes,
                         _redirect_uris=redirect_uris)
    db.session.add_all(scopes)
    db.session.add_all(redirect_uris)
    db.session.add(client)
    db.session.commit()
    return client


def update_client_secret(client_id, client_secret):
    db.session.query(OAuthClient) \
        .filter_by(client_id=client_id) \
        .update(dict(client_secret=client_secret))
    db.session.commit()


def update_client_details(client_id, name, description):
    db.session.query(OAuthClient) \
        .filter_by(client_id=client_id) \
        .update(dict(name=name, description=description))
    db.session.commit()


def get_redirect_uris_by_client_id(client_id):
    uris = db.session.query(OAuthClientRedirect) \
        .filter_by(client_id=client_id).all()
    return [uri.redirect_uri for uri in uris]


def delete_redirect_uris(client_id, redirect_uri_list):
    db.session.query(OAuthClientRedirect) \
        .filter(OAuthClientRedirect.client_id == client_id,
                OAuthClientRedirect.redirect_uri.in_(redirect_uri_list)) \
        .delete(synchronize_session=False)
    db.session.commit()


def insert_redirect_uris(client_id, redirect_uri_list):
    redirect_uris = [OAuthClientRedirect(client_id=client_id,
                                         redirect_uri=redirect_uri)
                     for redirect_uri in redirect_uri_list]
    db.session.add_all(redirect_uris)
    db.session.commit()


def get_scopes_by_client_id(client_id):
    scopes = db.session.query(OAuthClientScope) \
        .filter_by(client_id=client_id).all()
    return [Scopes[scope.scope] for scope in scopes]


def delete_scopes(client_id, scopes_list):
    scopes = [scope.name for scope in scopes_list]
    db.session.query(OAuthClientScope) \
        .filter(OAuthClientScope.client_id == client_id,
                OAuthClientScope.scope.in_(scopes)) \
        .delete(synchronize_session=False)
    db.session.commit()


def insert_scopes(client_id, scopes_list):
    scopes = [OAuthClientScope(client_id=client_id,
                               scope=scope.name)
              for scope in scopes_list]
    db.session.add_all(scopes)
    db.session.commit()
