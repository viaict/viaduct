from authlib.flask.oauth2 import ResourceProtector
from flask import abort, make_response
from flask_login import current_user
from functools import wraps

from app.service import role_service


def require_role(*roles):
    def real_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if role_service.user_has_role(current_user, *roles):
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
            return f(*args, **kwargs)

    return wrapper


def response_headers(headers=None):
    if headers is None:
        headers = dict()

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp

        return wrapper

    return decorator


# TODO Check.
require_oauth = ResourceProtector()
