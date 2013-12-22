from flask import Blueprint, abort, redirect, url_for
from flask.ext.login import current_user

from viaduct import application, db

blueprint = Blueprint('ideal', __name__, url_prefix='/ideal')

@blueprint.route('/')
def ideal_overview():
	return abort(404)
