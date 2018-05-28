import re

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
    auto_approve = db.Column(db.Boolean(), default=False, nullable=False)

    # TODO image, first create image upload feature.

    # TODO? allowed request types?

    _redirect_uris = db.relationship("OAuthClientRedirect")
    _default_scopes = db.relationship("OAuthClientScope")

    @property
    def client_type(self):
        """According to RFC 6749: 2.1. Client Types."""
        if self.confidential:
            return 'confidential'
        return 'public'

    def validate_redirect_uri(self, uri):
        return any(re.match(allowed, uri) for allowed in self.redirect_uris)

    @property
    def redirect_uris(self):
        return [uri.redirect_uri for uri in self._redirect_uris]

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        return [scope.scope for scope in self._default_scopes]


class OAuthClientRedirect(db.Model):
    __tablename__ = "oauth_client_redirect"

    id = db.Column(db.Integer, primary_key=True)
    client = db.relationship("OAuthClient")
    client_id = db.Column(db.String(64),
                          db.ForeignKey("oauth_client.client_id",
                                        ondelete="cascade"))
    redirect_uri = db.Column(db.String(256))


class OAuthClientScope(db.Model):
    __tablename__ = "oauth_client_scope"

    id = db.Column(db.Integer, primary_key=True)
    client = db.relationship("OAuthClient")
    client_id = db.Column(db.String(64),
                          db.ForeignKey("oauth_client.client_id",
                                        ondelete="cascade"))
    scope = db.Column(db.String(256))
