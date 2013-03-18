import validictory

from flask import request
from flask.ext.restful import Resource

from viaduct import api_manager, db
from viaduct.helpers.api import make_api_response
from viaduct.models import Course, Education

class CourseAPI(Resource):
	@staticmethod
	def register():
		api_manager.add_resource(CourseAPI, '/api/courses', '/api/courses/',
			'/api/courses/<int:course_id>', '/api/courses/<int:course_id>/')

	@staticmethod
	def get(course_id=None):
		if course_id:
			course = Course.query.get(course_id)

			if not course:
				return make_api_response(400, 'No object has been associated with the course ID that has been specified.')

			return course.to_dict()
		else:
			results = []

			for course in Course.query.all():
				results.append(course.to_dict())

			return results

	@staticmethod
	def post():
		data = request.json
		schema = {'type': 'object', 'properties':
			{'education_id': {'type': 'integer'},
			'name': {'type': 'string'},
			'description': {'type': 'string'}}
		}

		try:
			validictory.validate(data, schema)
		except Exception:
			return make_api_response(400, 'Data does not correspond to scheme.')

		if Education.query.filter(Education.id==data['education_id']).count() == 0:
			return make_api_response(400, 'No object has been associated with the education ID that has been specified.')

		if Course.query.filter(Course.name==data['name']).count() > 0:
			return make_api_response(400, 'There is already an object with the name that has been specified.')

		course = Course(data['name'], data['description'])
		db.session.add(course)
		db.session.commit()

		return course.to_dict(), '201 The object has been created.'

	@staticmethod
	def delete():
		data = request.json
		schema = {'type': 'array', 'items': {'type': 'integer'}}

		print(data)

		try:
			validictory.validate(data, schema)
		except Exception:
			return make_api_response(400, 'Data does not correspond to scheme.')

		return data

