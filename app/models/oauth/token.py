import time

from authlib.flask.oauth2 import sqla

from app import db


class OAuthToken(db.Model, sqla.OAuth2TokenMixin):
    __tablename__ = 'oauth_token'

    id = db.Column(db.Integer, primary_key=True)

    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def is_refresh_token_expired(self):
        """Refresh tokens expire within a month."""
        return (self.issued_at + 2592000) < time.time()
