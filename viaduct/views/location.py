from flask import Blueprint, flash, redirect, render_template, request, \
		url_for, jsonify

from viaduct import db
from viaduct.models.location import Location
from viaduct.utilities import serialize_sqla

blueprint = Blueprint('location', __name__)

@blueprint.route('/locations/<int:location_id>/contacts/', methods=['GET'])
def get_contacts(location_id):
	location = Location.query.get(location_id)
	return jsonify(contacts=serialize_sqla(location.contacts.all()))