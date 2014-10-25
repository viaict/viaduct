import validictory

from flask import request

from viaduct import application, db
from viaduct.helpers import Resource
from viaduct.helpers.api import make_api_response
from viaduct.models import Course, Education


class CourseAPI(Resource):
    @staticmethod
    def register():
        view = CourseAPI.as_view('course_api')

        application.add_url_rule('/api/courses/', view_func=view,
                                 methods=['DELETE', 'GET', 'POST'])

    @staticmethod
    def get():
        data = request.json
        schema = {
            'type': 'object',
            'properties': {
                'id': {'type': [
                    {'type': 'null'},
                    {'type': 'integer'},
                    {'type': 'array', 'items': {'type': 'integer'}}
                ]},
            }
        }
        course_ids = []
        result = {}

        try:
            validictory.validate(data, schema)
        except Exception:
            return make_api_response(400,
                                     'Data does not correspond to scheme.')

        if isinstance(data['id'], list):
            course_ids = data['id']
        elif isinstance(data['id'], int):
            course_ids = [data['id']]

        query = Course.query

        if len(course_ids) > 0:
            query = query.filter(Course.id.in_(course_ids))

        result['courses'] = []

        for course in query.all():
            result['courses'].append(course.to_dict())

        return result

    @staticmethod
    def post():
        data = request.json
        schema = {'type': 'object',
                  'properties': {'education_id': {'type': 'integer'},
                                 'name': {'type': 'string'},
                                 'description': {'type': 'string'}}}

        try:
            validictory.validate(data, schema)
        except Exception:
            return make_api_response(400,
                                     'Data does not correspond to scheme.')

        if Education.query\
                .filter(Education.id == data['education_id']).count() == 0:
            return make_api_response(400, 'No object has been associated with '
                                     'the education ID that has been '
                                     'specified.')

        if Course.query.filter(Course.name == data['name']).count() > 0:
            return make_api_response(400, 'There is already an object with '
                                     'the name that has been specified.')

        course = Course(data['name'], data['description'])
        db.session.add(course)
        db.session.commit()

        return course.to_dict(), '201 The object has been created.'

    @staticmethod
    def delete():
        data = request.json
        schema = {'type': [{'type': 'integer'},
                           {'type': 'array', 'items': {'type': 'integer'}}]}

        try:
            validictory.validate(data, schema)
        except Exception:
            return make_api_response(400,
                                     'Data does not correspond to scheme.')

        return data
