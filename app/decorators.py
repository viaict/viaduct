from authlib.flask.oauth2 import ResourceProtector
from authlib.flask.oauth2 import current_token
from flask import make_response
from flask import request
from flask_login import current_user
from flask_restful import abort
from functools import wraps
from marshmallow import ValidationError

from app.service import role_service


def require_role(*roles):
    def real_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Prioritize access_tokens over flask_login.
            user = current_token.user if current_token else None
            if user is None:
                user = current_user
            if role_service.user_has_role(user, *roles):
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


def json_schema(schema):
    def real_decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if not request.is_json:
                abort(400)
            try:
                json = request.get_json(force=True)
                return f(self, schema.load(json), *args, **kwargs)
            except ValidationError as e:
                abort(400, errors=e.messages)

        return wrapper

    return real_decorator


_require_oauth = ResourceProtector()


def require_oauth(scope=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return _require_oauth(scope=scope.name)(f)(*args, **kwargs)

        return wrapped

    return decorator
