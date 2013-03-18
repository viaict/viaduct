from flask import Blueprint

blueprint = Blueprint('education', __name__)

@blueprint.route('/examination')
def view_examination():
	return 'Hello'

