import validictory

from flask import request

from viaduct import app, db
from viaduct.helpers import Resource
from viaduct.helpers.api import make_api_response

from viaduct.models import Degree


class DegreeAPI(Resource):
    @staticmethod
    def register():
        view = DegreeAPI.as_view('degree_api')

        app.add_url_rule('/api/degrees/', view_func=view,
                                 methods=['DELETE', 'GET', 'POST'])

    @staticmethod
    def get(degree_id=None):
        if degree_id:
            degree = Degree.query.get(degree_id)

            if not degree:
                return make_api_response(400, 'No object has been associated '
                                         'with the degree ID that has been '
                                         'specified.')

            return degree.to_dict()
        else:
            results = []

            for degree in Degree.query.all():
                results.append(degree.to_dict())

            return results

    @staticmethod
    def post():
        data = request.json
        schema = {'type': 'object',
                  'properties': {'name': {'type': 'string'},
                                 'abbreviation': {'type': 'string'}}}

        try:
            validictory.validate(data, schema)
        except Exception:
            return make_api_response(400,
                                     'Data does not correspond to scheme.')

        if Degree.query.filter(Degree.name == data['name']).count() > 0:
            return make_api_response(400, 'There is already an object with '
                                     'the name that has been specified.')

        degree = Degree(data['name'], data['abbreviation'])
        db.session.add(degree)
        db.session.commit()

        return degree.to_dict(), '201 The object has been created.'

    @staticmethod
    def delete(degree_id=None):
        if degree_id:
            degree = Degree.query.get(degree_id)

            if not degree:
                return make_api_response(400, 'No object has been associated '
                                         'with the degree ID that has been '
                                         'specified')

            db.session.delete(degree)
            db.session.commit()

            return make_api_response(204, 'The object has been deleted')
        else:
            return make_api_response(400, 'TODO')
