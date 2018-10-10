from marshmallow import Schema, RAISE, fields, validates, ValidationError, \
    pre_dump


class PaginatedResponseSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    page = fields.Integer()
    page_size = fields.Integer()
    page_count = fields.Integer()

    data = fields.Method("get_data", many=True)

    def __init__(self, subschema, *args, **kwargs):
        super(PaginatedResponseSchema, self).__init__(*args, **kwargs)
        self.subschema = subschema

    @pre_dump
    def unpack_pagination(self, pagination_obj):
        return {
            'page': pagination_obj.page,
            'page_size': pagination_obj.per_page,
            'page_count': pagination_obj.pages,
            'data': pagination_obj.items
        }

    def get_data(self, obj):
        return self.subschema.dump(obj['data'])


class PaginatedSearchSchema(Schema):
    class Meta:
        missing = RAISE
        ordered = True

    search = fields.Str(missing='')
    page = fields.Integer(missing=1)

    @validates('page')
    def validate_age(self, data):
        if data <= 0:
            raise ValidationError('Page numbering starts at 0')
