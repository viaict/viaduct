from marshmallow import pre_dump, fields, Schema

from app.exceptions.base import ValidationException, ApplicationException


class InvalidMinuteException(ValidationException):
    class ErrorSchema(ApplicationException.ErrorSchema):
        class _InvalidLineSchema(Schema):
            line = fields.Integer()
            error = fields.String()
            details = fields.String()

        @pre_dump
        def transform_fields(self, obj):
            obj.line_errors = []
            iterator = {'unknown_task': obj.unknown_task_lines,
                        'missing_colon': obj.missing_colon_lines,
                        'unknown_users': obj.unknown_users}

            for key, errors in iterator.items():
                for line, detail in errors:
                    obj.line_errors.append({'line': line,
                                            'error': key,
                                            'details': detail})
            obj.line_errors.sort(key=lambda o: o['line'])

            return obj

        line_errors = fields.Nested(_InvalidLineSchema, many=True)

    message = "The minute was not according to semantic rules."
    type_ = "https://svia.nl/guides/user/pimpy"

    def __init__(self, missing_colon_lines, unknown_task_lines, unknown_users):
        self.unknown_task_lines = unknown_task_lines
        self.missing_colon_lines = missing_colon_lines
        self.unknown_users = unknown_users

        super().__init__({})
