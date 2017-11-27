from app import db


class OAuthGrant(db.Model):
    __tablename__ = 'oauth_grant'

    id = db.Column(db.Integer, primary_key=True)

    user = db.relationship('User')
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id', ondelete='CASCADE'))

    client = db.relationship("OAuthClient")
    client_id = db.Column(db.String(64),
                          db.ForeignKey('oauth_client.client_id'),
                          nullable=False)

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        from app.service import oauth_service
        oauth_service.delete_grant(self.id)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
