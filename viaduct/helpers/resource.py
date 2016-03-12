from flask import json, make_response, Response, request
from flask.views import MethodView
from viaduct import app
import re


def unpack(value):
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value

        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value

        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}


def output_json(data, code, headers):
    response = make_response(json.dumps(data), code)
    response.headers.extend(headers or {})

    return response


def get_all_routes():
    base_url_regex = r"^(/[^<>]*)(/<.*>)*/?"
    rv = []
    for route in app.url_map.iter_rules():
        rv.append(
            re.compile(base_url_regex).match(route.rule).group(1)
            .rstrip('/'))
    return set(rv)


class Resource(MethodView):
    @staticmethod
    def register():
        pass

    def dispatch_request(self, *args, **kwargs):
        method = getattr(self, request.method.lower(), None)

        if method is None and request.method == 'HEAD':
            method = getattr(self, 'get', None)

        assert method is not None, 'Unimplemented method %r' % request.method

        response = method(*args, **kwargs)

        if isinstance(response, Response):
            return response

        data, code, headers = unpack(response)
        response = output_json(data, code, headers)
        response.headers['Content-type'] = 'app/json'

        return response
