from flask_login import current_user

from app.service import role_service


def has_role(role):
    def real_decorator(f):
        def wrapper(*args, **kwargs):
            role_service.has_role(current_user, role)
            f(*args, **kwargs)

        return wrapper

    return real_decorator
