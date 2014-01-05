from flask.ext.login import current_user
from flask import jsonify

import requests
import json

from viaduct import db, application

MOLLIE_URL = application.config['MOLLIE_URL']
MOLLIE_TEST_KEY = application.config['MOLLIE_TEST_KEY']
MOLLIE_KEY = application.config['MOLLIE_KEY']

class MollieAPI:
	@staticmethod
	def create_transaction(amount, description="some via Mollie transaction"):
		auth_header = {'Authorization':'Bearer ' + MOLLIE_TEST_KEY}
		data = {
			'amount': amount,
			'redirectUrl':'http://svia.nl/mollie_test',
			'description': description
		}

		r = requests.post(MOLLIE_URL, headers=auth_header, data=data)
		return json.dumps(r.json, indent=4)

