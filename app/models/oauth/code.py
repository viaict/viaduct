from authlib.flask.oauth2.sqla import OAuth2AuthorizationCodeMixin

from app import db


class OAuthAuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth_authorization_code'

    id = db.Column(db.Integer, primary_key=True)

    user = db.relationship('User')
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id', ondelete='CASCADE'))
