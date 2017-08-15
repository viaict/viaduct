import validictory

from flask import request

from app import app, db
from app.utils.resource import Resource
from app.utils.api import make_api_response
from app.models.education import Education


class EducationAPI(Resource):
    @staticmethod
    def register():
        view = EducationAPI.as_view('education_api')

        app.add_url_rule('/api/educations/', view_func=view,
                         methods=['DELETE', 'GET', 'POST'])

    @staticmethod
    def get(education_id=None):
        if education_id:
            education = Education.query.get(education_id)

            if not education:
                return make_api_response(400, 'No object has been associated '
                                         'with the education ID that has been '
                                         'specified.')

            return education.to_dict()
        else:
            results = []

            for education in Education.query.all():
                results.append(education.to_dict())

            return results

    @staticmethod
    def post():
        data = request.get_json()
        schema = {'type': 'object',
                  'properties': {'name': {'type': 'string'}}}

        try:
            validictory.validate(data, schema)
        except Exception:
            return make_api_response(400,
                                     'Data does not correspond to scheme.')

        if Education.query.filter(Education.name == data['name']).count() > 0:
            return make_api_response(400, 'There is already an object with '
                                     'the name that has been specified.')

        education = Education(data['name'])
        db.session.add(education)
        db.session.commit()

        return make_api_response(201, 'The object has been created.')
