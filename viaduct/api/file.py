import validictory

from flask import json, Response, request
from flask.views import MethodView

from viaduct import application, db
from viaduct.helpers import Resource
from viaduct.helpers.api import make_api_response
from viaduct.models import File

class FileAPI(Resource):
	@staticmethod
	def register():
		view = FileAPI.as_view('file_api')

		application.add_url_rule('/api/files/', view_func=view,
			methods=['DELETE', 'GET', 'POST'])

	@staticmethod
	def delete():
		return {'hello', 'world'}

	@staticmethod
	def get():
		return {'hello', 'world'}

	@staticmethod
	def post():
		return {'hello', 'world'}

	@staticmethod
	def put():
		return {'hello', 'world'}

