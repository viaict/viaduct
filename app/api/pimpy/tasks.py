from authlib.flask.oauth2 import current_token
from flask_restful import Resource, abort
from marshmallow import Schema, fields, RAISE, pre_dump, validate, \
    ValidationError

from app import Roles
from app.decorators import require_oauth, require_role, json_schema
from app.exceptions import ValidationException
from app.oauth_scopes import Scopes
from app.service import pimpy_service, group_service

status_raw = ["new", "started", "done", "remove", "finished", "deleted"]


def dump_status(obj):
    return status_raw[obj.status]


def load_status(value):
    try:
        return status_raw.index(value)
    except ValueError as e:
        raise ValidationError(f"'{value}' not valid for status.") from e


class TaskSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    # List view
    b32_id = fields.String(dump_only=True)
    title = fields.String(required=True)
    group_id = fields.Integer(required=True)
    status = fields.Function(serialize=dump_status,
                             deserialize=load_status,
                             missing=lambda: load_status('new'))

    # Detail view
    created = fields.Date(dump_only=True)
    modified = fields.Date(dump_only=True)
    users = fields.List(fields.String(),
                        attribute='users_names',
                        validate=validate.Length(min=1),
                        required=True)
    content = fields.String()
    minute_id = fields.Integer(dump_only=True)
    line = fields.Integer(dump_only=True)

    @pre_dump
    def transform_fields(self, task):
        task.users_names = [user.name for user in task.users]
        return task

    @classmethod
    def get_list_schema(cls):
        return cls(many=True,
                   only=('b32_id', 'status', 'title', 'group_id', 'users'))


class TaskResource(Resource):
    schema_get = TaskSchema()
    schema_patch = TaskSchema(partial=True)

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self, task_id):
        task = pimpy_service.find_task_by_b32_id(task_id)

        pimpy_service.check_user_can_access_task(current_token.user, task)

        return self.schema_get.dump(task)

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_WRITE)
    @json_schema(schema=schema_patch)
    def patch(self, task_update, task_id):
        task = pimpy_service.get_task_by_b32_id(task_id)

        pimpy_service.check_user_can_access_task(current_token.user, task)

        pimpy_service.edit_task_property(
            task=task,
            content=task_update.get('content'),
            title=task_update.get('title'),
            users_property=','.join(task_update.get('users_names')))

        if 'status' in task_update:
            pimpy_service.set_task_status(task, task_update['status'])

        return self.get(task_id)


class TaskListResource(Resource):
    schema_get = TaskSchema.get_list_schema()
    schema_post = TaskSchema()

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self):
        tasks = pimpy_service.get_all_tasks_for_user(current_token.user)
        tasks = [task.task for task in tasks]
        return self.schema_get.dump(tasks)

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_WRITE)
    @json_schema(schema_post)
    def post(self, task: dict):

        # Check group permissions
        group = group_service.get_group_by_id(task['group_id'])
        if group not in group_service.get_groups_for_user(current_token.user):
            # TODO Centralize the errors in the application.
            abort(403, error=f'User not in group identified with {group.name}')

        try:
            new_task = pimpy_service.add_task_by_user_string(
                title=task['title'],
                content=task['content'],
                group_id=group.id,
                users_text=','.join(task['users_names']),
                line=None,
                minute=None,
                status=task['status'])
            return self.schema_post.dump(new_task), 201
        except ValidationException as e:
            abort(409, errors=e.details)


class GroupTaskListResource(Resource):
    schema_get = TaskSchema.get_list_schema()

    @require_oauth(Scopes.pimpy)
    @require_role(Roles.PIMPY_READ)
    def get(self, group_id):
        if not current_token.user.member_of_group(group_id):
            # TODO Centralize the errors in the application.
            abort(403, error=f'user not in group identified with {group_id}')

        tasks = pimpy_service.get_all_tasks_for_group(group_id)
        tasks = [task.task for task in tasks]
        return self.schema_get.dump(tasks)
