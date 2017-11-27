from app import db


class OAuthToken(db.Model):
    __tablename__ = 'oauth_token'

    id = db.Column(db.Integer, primary_key=True)

    client = db.relationship("OAuthClient")
    client_id = db.Column(db.String(64),
                          db.ForeignKey('oauth_client.client_id'),
                          nullable=False)

    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    token_type = db.Column(db.String(64))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
