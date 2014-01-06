from flask.ext.login import current_user
from flask import jsonify, redirect, url_for
from viaduct.models.mollie import Transaction

import requests
import json
import datetime

from viaduct import db, application

MOLLIE_URL = application.config['MOLLIE_URL']
MOLLIE_TEST_KEY = application.config['MOLLIE_TEST_KEY']
MOLLIE_KEY = application.config['MOLLIE_KEY']
MOLLIE_REDIRECT_URL = application.config['MOLLIE_REDIRECT_URL']

class MollieAPI:
	@staticmethod
	def create_transaction(amount, description, local_url=""):
		transaction = Transaction(amount=amount, description=description,\
			user=current_user)
		db.session.add(transaction)
		db.session.commit()

		auth_header = {'Authorization':'Bearer ' + MOLLIE_TEST_KEY}
		data = {
			'amount': amount,
			'redirectUrl': MOLLIE_REDIRECT_URL + str(transaction.id),
			'description': description,
			'metadata': {
				'localUrl': local_url
			}
		}

		r = requests.post(MOLLIE_URL, headers=auth_header, data=data)
		print r.json
		transaction.mollie_id = r.json['id']
		transaction.createdDatetime = datetime.datetime.strptime(r.json['createdDatetime'], "%Y-%m-%dT%H:%M:%S.0Z")
		transaction.status = r.json['status']
		db.session.commit()
		print r.json['amount']
		print r.json['links']['paymentUrl']
		return redirect(r.json['links']['paymentUrl'])

	@staticmethod
	def check_transaction(trans_id):
		transaction = Transaction.query.filter(Transaction.id==trans_id).first()

		auth_header = {'Authorization':'Bearer ' + MOLLIE_TEST_KEY}
		r = requests.get(MOLLIE_URL + transaction.mollie_id, headers=auth_header)
		print MOLLIE_URL + transaction.mollie_id
		print r.json
		transaction.status = r.json['status']
		if 'expiredDatetime' in r.json:
			transaction.expiredDatetime = datetime.datetime.strptime(r.json['expiredDatetime'], "%Y-%m-%dT%H:%M:%S.0Z")
		if 'cancelledDatetime' in r.json:
			transaction.cancelledDatetime = datetime.datetime.strptime(r.json['cancelledDatetime'], "%Y-%m-%dT%H:%M:%S.0Z")
		db.session.commit()
		if transaction.status == 'paid':
			return True, 'De transactie is afgerond.'
		elif transaction.status == 'open':
			return False, 'De transactie is nog bezig.'
		return False, 'De transactie is afgebroken.'

	@staticmethod
	def get_all_transactions():
		transactions = Transaction.query.all()
		return transactions
