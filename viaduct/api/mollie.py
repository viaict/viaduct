from flask.ext.login import current_user
from flask import json()ify, redirect, url_for
from viaduct.models.mollie import Transaction
from viaduct.api.custom_form import CustomFormAPI

import requests
import json()
import datetime

from viaduct import db, application

MOLLIE_URL = application.config['MOLLIE_URL']
MOLLIE_REDIRECT_URL = application.config['MOLLIE_REDIRECT_URL']
if application.config['MOLLIE_TEST_MODE']:
	MOLLIE_KEY = application.config['MOLLIE_TEST_KEY']
	print 'USING MOLLIE TEST KEY'
else:
	MOLLIE_KEY = application.config['MOLLIE_KEY']
	print 'USING MOLLIE LIVE KEY'

class MollieAPI:
	@staticmethod
	def create_transaction(amount, description, local_url="", user=current_user):
		amount += 0.99
		transaction = Transaction(amount=amount, description=description,\
			user=user)
		db.session.add(transaction)
		db.session.commit()

		auth_header = {'Authorization':'Bearer ' + MOLLIE_KEY}
		data = {
			'amount': amount,
			'redirectUrl': MOLLIE_REDIRECT_URL + str(transaction.id),
			'description': description,
			'metadata': {
				'localUrl': local_url
			}
		}

		r = requests.post(MOLLIE_URL, headers=auth_header, data=data)
		print r.json()
		transaction.mollie_id = r.json()['id']
		transaction.createdDatetime = datetime.datetime.strptime(r.json()['createdDatetime'], "%Y-%m-%dT%H:%M:%S.0Z")
		transaction.status = r.json()['status']
		db.session.commit()
		print r.json()['amount']
		print r.json()['links']['paymentUrl']
		return r.json()['links']['paymentUrl'], transaction

	@staticmethod
	def get_payment_url(transaction_id=0, mollie_id=""):
		auth_header = {'Authorization':'Bearer ' + MOLLIE_KEY}
		if transaction_id:
			transaction = Transaction.query.filter(Transaction.id==transaction_id).first()
		else:
			transaction = Transaction.query.filter(Transaction.mollie_id==mollie_id).first()
		r = requests.get(MOLLIE_URL + transaction.mollie_id, headers=auth_header)
		if 'error' in r.json():
			return False, r.json()['error']['message']
		if 'paymentUrl' in r.json()['links']:
			return r.json()['links']['paymentUrl']
		else:
			return r.json()['links']['redirectUrl']


	@staticmethod
	def check_transaction(transaction_id=0, mollie_id=""):
		if transaction_id:
			transaction = Transaction.query.filter(Transaction.id==transaction_id).first()
		else:
			transaction = Transaction.query.filter(Transaction.mollie_id==mollie_id).first()

		auth_header = {'Authorization':'Bearer ' + MOLLIE_KEY}
		r = requests.get(MOLLIE_URL + transaction.mollie_id, headers=auth_header)
		if 'error' in r.json():
			return False, r.json()['error']['message']
		print MOLLIE_URL + transaction.mollie_id
		print r.json()
		transaction.status = r.json()['status']
		if 'expiredDatetime' in r.json():
			transaction.expiredDatetime = datetime.datetime.strptime(r.json()['expiredDatetime'], "%Y-%m-%dT%H:%M:%S.0Z")
		if 'cancelledDatetime' in r.json():
			transaction.cancelledDatetime = datetime.datetime.strptime(r.json()['cancelledDatetime'], "%Y-%m-%dT%H:%M:%S.0Z")
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
