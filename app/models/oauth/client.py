from authlib.flask.oauth2.sqla import OAuth2ClientMixin
from sqlalchemy.ext.hybrid import hybrid_property

from app import db


class OAuthClient(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth_client'

    # Overwrite the mixin client_id, since we want it to be the primary key.
    client_id = db.Column(db.String(48), primary_key=True)

    # Creator of the client
    user = db.relationship("User")
    user_id = db.Column(db.ForeignKey("user.id"))

    auto_approve = db.Column(db.Boolean(), default=False, nullable=False)

    @hybrid_property
    def scopes(self):
        if self.scope:
            return self.scope.splitlines()
        return []
