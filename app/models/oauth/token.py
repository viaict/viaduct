from app import db


class OAuthToken(db.Model):
    __tablename__ = 'oauth_token'

    id = db.Column(db.Integer, primary_key=True)

    client = db.relationship("OAuthClient")
    client_id = db.Column(db.String(64),
                          db.ForeignKey('oauth_client.client_id',
                                        ondelete="cascade"),
                          nullable=False)

    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    token_type = db.Column(db.String(64))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.relationship("OAuthTokenScope")

    @property
    def scopes(self):
        return [scope.scope for scope in self._scopes]

    def delete(self):
        from app.service import oauth_service
        oauth_service.delete_token(self.id)


class OAuthTokenScope(db.Model):
    __tablename__ = "oauth_token_scope"

    id = db.Column(db.Integer, primary_key=True)
    token = db.relationship("OAuthToken")
    token_id = db.Column(db.Integer,
                         db.ForeignKey("oauth_token.id", ondelete='cascade'))
    scope = db.Column(db.String(256))
