from flask import json, make_response, Response, request
from flask.views import MethodView

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

class Resource(MethodView):
	def dispatch_request(self, *args, **kwargs):
		method = getattr(self, request.method.lower(), None)

		if method is None and request.method == 'HEAD':
			method = getattr(self, 'get', None)

		assert method is not None, 'Unimplemented method %r' % request.method

		response = method(*args, **kwargs)

		if isinstance(response, Response):
			return response

		data, code, headers = unpack(response)
		print(data)
		response = output_json(data, code, headers)
		response.headers['Content-type'] = 'application/json'

		return response

