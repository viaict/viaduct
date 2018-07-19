from app.exceptions.base import ValidationException


class InvalidMinuteException(ValidationException):
    def __init__(self, missing_colon_lines, unknown_task_lines, unknown_users,
                 **kwargs):
        self.unknown_task_lines = unknown_task_lines
        self.missing_colon_lines = missing_colon_lines
        self.unknown_users = unknown_users

        details = {
            'missing_colon': missing_colon_lines,
            'unknown_task': unknown_task_lines,
            'unknown_users': unknown_users
        }

        super().__init__(details=details, **kwargs)
