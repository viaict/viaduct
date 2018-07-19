from authlib.flask.oauth2 import current_token
from flask_restful import Resource, abort
from marshmallow import Schema, fields, pre_dump, RAISE, validate, \
    ValidationError, validates

from app import Roles
from app.decorators import require_oauth, require_role, json_schema
from app.exceptions.pimpy import InvalidMinuteException
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


class MinuteErrorSchema(Schema):
    class InvalidLineSchema(Schema):
        line = fields.Integer()
        error = fields.String()
        details = fields.String()

    @pre_dump
    def transform_fields(self, details):
        errors = []
        print(details)
        for key in details:
            for line, detail in details[key]:
                errors.append({'line': line,
                               'error': key,
                               'details': detail})
        return {'errors': errors}

    errors = fields.Nested(InvalidLineSchema, many=True)


class MinuteResource(Resource):
    schema_get = MinuteSchema()

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self, minute_id):
        minute = pimpy_service.find_minute_by_id(minute_id)

        pimpy_service.check_user_can_access_minute(current_token.user, minute)

        return self.schema_get.dump(minute)


class GroupMinuteResource(Resource):
    schema_get = MinuteSchema.get_list_schema()
    schema_post = MinuteSchema()
    schema_post_error = MinuteErrorSchema()

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self, group_id):
        minutes = pimpy_service.get_minutes_for_group(group_id)

        if not current_token.user.member_of_group(group_id):
            # TODO Centralize the errors in the application.
            abort(403, error=f'user not in group identified with {group_id}')

        return self.schema_get.dump(minutes)

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_WRITE)
    @json_schema(schema_post)
    def post(self, new_minute: dict, group_id: int):
        group = group_service.get_group_by_id(group_id)

        if group not in group_service.get_groups_for_user(current_token.user):
            # TODO Centralize the errors in the application.
            abort(403, error=f'User not in group identified with {group.name}')
        try:
            minute = pimpy_service.add_minute(
                content='\n'.join(new_minute['content_lines']),
                date=new_minute['minute_date'],
                group=group)
        except InvalidMinuteException as e:
            return self.schema_post_error.dump(e.details), 400

        return self.schema_post.dump(minute), 201
