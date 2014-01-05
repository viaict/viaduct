from flask import Blueprint, abort, redirect, url_for, jsonify
from flask.ext.login import current_user
from viaduct.api.mollie import MollieAPI
import requests
import json

from viaduct import application, db

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')

@blueprint.route('/json_test')
def json_test():
	url = 'https://api.github.com/users/tzwaan'
	r = requests.get(url)
	return json.dumps(r.json, indent=4)

@blueprint.route('/mollie_test')
def mollie_test():

	return MollieAPI.create_transaction(49.83, 'de eerste transactie')
