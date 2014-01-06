from flask.ext.login import current_user
from flask import jsonify
from viaduct.models.mollie import Transaction

import requests
import json

from viaduct import db, application

MOLLIE_URL = application.config['MOLLIE_URL']
MOLLIE_TEST_KEY = application.config['MOLLIE_TEST_KEY']
MOLLIE_KEY = application.config['MOLLIE_KEY']

class MollieAPI:
	@staticmethod
	def create_transaction(amount, description="some via Mollie transaction"):
		transaction = Transaction(amount=amount, description=description)
		db.session.add(transaction)
		db.session.commit()

		auth_header = {'Authorization':'Bearer ' + MOLLIE_TEST_KEY}
		data = {
			'amount': amount,
			'redirectUrl':'http://svia.nl/mollie/succes/' + str(transaction.id),
			'description': description
		}

		r = requests.post(MOLLIE_URL, headers=auth_header, data=data)
		print json.dumps(r.json).amount
		return json.dumps(r.json, indent=4)

