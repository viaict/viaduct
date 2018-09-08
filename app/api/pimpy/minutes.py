from authlib.flask.oauth2 import current_token
from flask_restful import Resource
from marshmallow import Schema, fields, pre_dump, RAISE, validate, \
    ValidationError, validates

from app import Roles
from app.decorators import require_oauth, require_role, json_schema
from app.oauth_scopes import Scopes
from app.service import pimpy_service, group_service


class MinuteSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    id = fields.Integer(dump_only=True)
    created = fields.Date(dump_only=True)
    minute_date = fields.Date(data_key='date', required=True)
    content = fields.List(fields.String(missing=""),
                          attribute='content_lines',
                          validate=validate.Length(min=1),
                          required=True)
    group_id = fields.Integer(required=True)

    @pre_dump
    def transform_fields(self, minute):
        minute.content_lines = minute.content.splitlines()
        return minute

    @classmethod
    def get_list_schema(cls):
        return cls(many=True,
                   only=('id', 'group_id', 'minute_date'))

    @validates('content')
    def validate_empty_content(self, value):
        if '\n'.join(value).strip() == "":
            raise ValidationError("Minute content is empty")


class MinuteResource(Resource):
    schema_get = MinuteSchema()

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self, minute_id):
        minute = pimpy_service.get_minute_by_id(minute_id)

        pimpy_service.check_user_can_access_minute(current_token.user, minute)

        return self.schema_get.dump(minute)


class GroupMinuteResource(Resource):
    schema_get = MinuteSchema.get_list_schema()
    schema_post = MinuteSchema()

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self, group_id):
        group_service.check_user_member_of_group(current_token.user, group_id)

        minutes = pimpy_service.get_minutes_for_group(group_id)

        return self.schema_get.dump(minutes)

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_WRITE)
    @json_schema(schema_post)
    def post(self, new_minute: dict, group_id: int):
        group_service.check_user_member_of_group(current_token.user, group_id)

        group = group_service.get_group_by_id(group_id)

        minute = pimpy_service.add_minute(
            content='\n'.join(new_minute['content_lines']),
            date=new_minute['minute_date'],
            group=group)

        return self.schema_post.dump(minute), 201
