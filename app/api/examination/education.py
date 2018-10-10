from flask_restful import Resource
from http import HTTPStatus
from marshmallow import Schema, RAISE, fields

from app import Roles
from app.api.schema import PaginatedResponseSchema, PaginatedSearchSchema
from app.decorators import require_oauth, require_role, query_parameter_schema
from app.oauth_scopes import Scopes
from app.service import examination_service


class EducationSchema(Schema):
    class Meta:
        missing = RAISE
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String()
    description = fields.String()


class EducationResource(Resource):

    @require_oauth(Scopes.examination)
    @require_role(Roles.EXAMINATION_WRITE)
    # @json_schema(schema_post_delete)
    def post(self, data, group_id: int):
        raise NotImplementedError()

    @require_oauth(Scopes.examination)
    @require_role(Roles.EXAMINATION_WRITE)
    def delete(self, education_id: int):
        examination_service.delete_education(education_id)
        return '', HTTPStatus.NO_CONTENT


class EducationListResource(Resource):
    schema_get = PaginatedResponseSchema(EducationSchema(many=True))
    schema_search = PaginatedSearchSchema()

    @require_oauth(Scopes.examination)
    @require_role(Roles.EXAMINATION_WRITE)
    @query_parameter_schema(schema_search)
    def get(self, search, page):
        pagination = examination_service.paginated_search_educations(
            search=search, page=page)

        return self.schema_get.dump(pagination)
