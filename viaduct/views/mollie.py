from flask import Blueprint, abort, redirect, url_for, jsonify, \
	render_template, request
from flask.ext.login import current_user
from viaduct.api.mollie import MollieAPI
from viaduct.api.group import GroupPermissionAPI
import requests
import json

from viaduct import application, db

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')

@blueprint.route('/create', methods=['GET', 'POST'])
def create_mollie_transaction():
	amount = request.form['amount']
	description = request.form['description']
	local_url = request.form['local_url']
	return MollieAPI.create_transaction(amount, description, local_url)

@blueprint.route('/success')
@blueprint.route('/success/<transaction_id>', methods=['GET', 'POST'])
def mollie_succes(transaction_id=0):
	success, message = MollieAPI.check_transaction(transaction_id)
	return render_template('mollie/success.htm', message=message)

@blueprint.route('/view/')
def view_all_transactions():
	if not GroupPermissionAPI.can_read('mollie'):
		return abort(403)
	transactions = MollieAPI.get_all_transactions()
	return render_template('mollie/view.htm', transactions=transactions)

