from flask_restful import Resource
from http import HTTPStatus
from marshmallow import Schema, RAISE, fields

import app.service.group_service
from app import Roles
from app.api.schema import PaginatedResponseSchema, PaginatedSearchSchema
from app.api.user.user import UserSchema
from app.decorators import require_oauth, require_role, json_schema, \
    query_parameter_schema
from app.oauth_scopes import Scopes
from app.service import group_service


class UserIdListGroupUserSchema(Schema):
    class Meta:
        missing = RAISE
        ordered = True

    user_ids = fields.List(fields.Integer(), required=True)


class GroupUserListResource(Resource):
    schema_get = PaginatedResponseSchema(UserSchema.get_list_schema())
    schema_search = PaginatedSearchSchema()
    schema_post_delete = UserIdListGroupUserSchema()

    @require_oauth(Scopes.group)
    @require_role(Roles.GROUP_READ)
    @query_parameter_schema(schema_search)
    def get(self, search, page, group_id):
        pagination = app.service.group_service.paginated_search_group_users(
            group_id=group_id, search=search, page=page)

        return self.schema_get.dump(pagination)

    @require_oauth(Scopes.group)
    @require_role(Roles.GROUP_WRITE)
    @json_schema(schema_post_delete)
    def post(self, data, group_id: int):
        user_ids = data.get('user_ids')
        group_service.add_group_users(group_id, user_ids)
        return '', HTTPStatus.NO_CONTENT

    @require_oauth(Scopes.group)
    @require_role(Roles.GROUP_WRITE)
    @json_schema(schema_post_delete)
    def delete(self, data, group_id: int):
        user_ids = data.get('user_ids')
        group_service.remove_group_users(group_id, user_ids)
        return '', HTTPStatus.NO_CONTENT
