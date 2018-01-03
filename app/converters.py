
from werkzeug.routing import ValidationError, BaseConverter

from app import app
from app.service import alv_service


class ModelIdConverter(BaseConverter):
    """
    URL converter that resolves id to a model and returns the model.
    """

    def __init__(self, url_map):
        super().__init__(url_map)
        self.regex = '\d+'

    def to_python(self, value):
        print("LOL2")
        intval = int(value)
        if not 0 < intval <= 2 ** 32:
            raise ValidationError()
        model = self.resolve_id(intval)
        if not model:
            raise ValidationError()
        return model

    def to_url(self, value):
        return str(value.id)

    def resolve_id(self, model_id):
        raise NotImplementedError()


class AlvConverter(ModelIdConverter):
    def resolve_id(self, alv_id):
        # from app import app
        # from app.service import alv_service
        with app.test_request_context():
            return alv_service.find_alv_by_id(alv_id)


def init_converters(app):
    app.url_map.converters['alv'] = AlvConverter
