from authlib.flask.oauth2 import current_token
from flask_restful import Resource
from marshmallow import Schema, fields

from app import Roles
from app.decorators import require_oauth, require_role
from app.exceptions.base import AuthorizationException
from app.oauth_scopes import Scopes
from app.service import role_service, user_service


class UserMembershipSchema(Schema):
    member = fields.Boolean(attribute='has_paid')
    paid_date = fields.Date(dump_only=True)
    honorary_member = fields.Boolean()
    favourer = fields.Boolean()


class UserMembershipResource(Resource):
    schema_get = UserMembershipSchema()

    @require_oauth(Scopes.user)
    def get(self, user_id: int):
        if user_id == current_token.user.id:
            return self.schema_get.dump(current_token.user)

        if not role_service.user_has_role(current_token.user, Roles.USER_READ):
            raise AuthorizationException(
                "You may not access use with user id {user_id}")
        else:
            user = user_service.get_user_by_id(user_id)
            return self.schema_get.dump(user)

    @require_oauth(Scopes.user)
    @require_role(Roles.USER_WRITE)
    def patch(self):
        """Update the membership status of an user."""
        raise NotImplementedError()
