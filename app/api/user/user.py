from authlib.flask.oauth2 import current_token
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_restful import Resource
from marshmallow import Schema, RAISE, fields, validates, ValidationError

from app import Roles
from app.api.schema import PaginatedSearchSchema, PaginatedResponseSchema
from app.decorators import require_oauth, require_role, json_schema, \
    query_parameter_schema
from app.exceptions.base import AuthorizationException
from app.oauth_scopes import Scopes
from app.service import user_service, role_service


class UserSchema(Schema):
    class Meta:
        missing = RAISE
        ordered = True

    id = fields.Integer(dump_only=True)

    # Login details
    email = fields.Email(required=True)
    disabled = fields.String(missing=False)

    first_name = fields.String(required=True)
    last_name = fields.String(required=True)

    favourer = fields.Boolean()
    member = fields.Boolean(attribute='has_paid')

    birth_date = fields.Date(required=True)
    phone_nr = fields.String()
    locale = fields.String()

    student_id = fields.Str(required=True)

    # TODO make education a int or a name?
    education_id = fields.Integer()
    study_start = fields.Date()
    alumnus = fields.Boolean(missing=False)

    @validates('birth_date')
    def validate_age(self, data):
        sixteen_years_ago = datetime.now().date() - relativedelta(years=16)

        if data < sixteen_years_ago:
            raise ValidationError('Users need to be at least 16 years old.')

    @classmethod
    def get_list_schema(cls):
        return cls(many=True,
                   only=('id', 'email', 'first_name', 'last_name',
                         'student_id', 'member', 'favourer'))


class UserResource(Resource):
    schema_get = UserSchema()

    @require_oauth()
    def get(self, user_id: int):
        if user_id == current_token.user.id:
            return self.schema_get.dump(current_token.user)

        if not role_service.user_has_role(
                current_token.user, Roles.USER_READ):
            raise AuthorizationException(
                f"You cannot access user with id {user_id}")

        user = user_service.get_user_by_id(user_id)
        return self.schema_get.dump(user)

    @require_oauth()
    def patch(self):
        # TODO confirmed student id cannot be changed.
        raise NotImplementedError()


class UserListResource(Resource):
    schema_get = PaginatedResponseSchema(UserSchema.get_list_schema())
    schema_search = PaginatedSearchSchema()
    schema_post = UserSchema()

    @require_oauth(Scopes.user)
    @require_role(Roles.USER_READ)
    @query_parameter_schema(schema_search)
    def get(self, search, page):
        pagination = user_service.paginated_search_all_users(
            search=search, page=page)

        return self.schema_get.dump(pagination)

    @require_oauth(Scopes.user)
    @require_role(Roles.USER_WRITE)
    @json_schema(schema_post)
    def post(self, new_user: dict):
        raise NotImplementedError()
