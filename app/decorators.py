from functools import wraps
from flask_login import current_user
from flask import abort

from app.service import role_service


def require_role(role):
    def real_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if role_service.user_has_role(current_user, role):
                return f(*args, **kwargs)
            else:
                abort(403)

        return wrapper

    return real_decorator


def require_membership(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous or not current_user.has_paid:
            abort(403)
        else:
            f(*args, **kwargs)

    return wrapper
