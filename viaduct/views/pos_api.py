# -*- coding: utf-8 -*-
from functools import wraps
from sqlalchemy import or_
from flask import request, Blueprint, jsonify

from viaduct import application
from viaduct.api.user import UserAPI
from viaduct.models.user import User


blueprint = Blueprint('pos_api', __name__, url_prefix='/api')


def requires_pos_api_key(func):

    @wraps(func)
    def decorated_func(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return jsonify(errors='Authorization key missing'), 401

        if auth and auth == application.config['POS_API_KEY']:
            # if auth and auth is 'A':
            return func(*args, **kwargs)
        else:
            return jsonify(errors='Authorization key invalid: ' + auth), 401
    return decorated_func


@blueprint.route('/get_members/', methods=['GET'])
@requires_pos_api_key
def get_members():
    data = {
        user.id: user.name for user in User.query.filter(
            or_(User.has_payed == True,  # noqa
                User.honorary_member == True,  # noqa
                User.favourer == True)  # noqa
        ).all()
    }
    return jsonify(data=data), 200


@requires_pos_api_key
@blueprint.route('/get_member_details/<int:_id>/', methods=['GET'])
def get_member_details(_id=None):
    if not id:
        return jsonify(errors='No user id given'), 400
    user = User.by_id(_id)
    if not user:
        return jsonify(errors='User not found with that id'), 404
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "avatar": UserAPI.avatar(user),
        "gender": user.gender,
        "locale": user.locale,
        "student_id": user.student_id,
        "education": user.education.name
    }
    return jsonify(data=data), 200
