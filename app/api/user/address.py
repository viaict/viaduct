from authlib.flask.oauth2 import current_token
from flask_restful import Resource
from marshmallow import Schema, fields

from app import Roles
from app.decorators import require_oauth
from app.exceptions.base import AuthorizationException
from app.oauth_scopes import Scopes
from app.service import role_service, user_service


class AddressSchema(Schema):
    address = fields.String(required=True)
    zip = fields.String(required=True)
    city = fields.String(required=True)
    country = fields.String(required=True)


class UserAddressResource(Resource):
    schema_get = AddressSchema()
    schema_post = AddressSchema(partial=True)

    @require_oauth(Scopes.user)
    def get(self, user_id: int):
        """Get the address details of the user."""

        if user_id == current_token.user.id:
            return self.schema_get.dump(current_token.user)
        if not role_service.user_has_role(current_token.user, Roles.USER_READ):
            raise AuthorizationException(
                f"User cannot access user with id {user_id}.")
        else:
            user = user_service.get_user_by_id(user_id)
            return self.schema_get.dump(user)

    @require_oauth
    def put(self, user_id: int, new_user_address: dict):
        """Put a completely new address for the user."""
        raise NotImplementedError()
