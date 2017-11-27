from app import db


class OAuthClient(db.Model):
    __tablename__ = 'oauth_client'

    # Human readable name/description (optional)
    name = db.Column(db.String(64))
    description = db.Column(db.String(512))

    # Creator of the client
    user = db.relationship("User")
    user_id = db.Column(db.ForeignKey("user.id"))

    # Client details
    client_id = db.Column(db.String(64), primary_key=True)
    client_secret = db.Column(db.String(64), unique=True, index=True,
                              nullable=False)

    confidential = db.Column(db.Boolean)

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        """According to RFC 6749: 2.1. Client Types"""
        if self.confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []
