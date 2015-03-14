from flask import Blueprint, abort
from viaduct.api import GroupPermissionAPI

from pprint import pprint

blueprint = Blueprint('queryduct', __name__, url_prefix='/queryduct')


@blueprint.route('/', methods=['GET'])
def main():
    if not GroupPermissionAPI.can_read('queryduct'):
        return abort(403)

    import viaduct.models as models_module
    from flask_sqlalchemy import _BoundDeclarativeMeta

    models = {}

    for obj in models_module.__dict__.values():
        if type(obj) is _BoundDeclarativeMeta:
            model_name = obj.__name__
            columns = obj.__table__.columns.keys()

            models[model_name] = columns

    pprint(models)

    return ''
