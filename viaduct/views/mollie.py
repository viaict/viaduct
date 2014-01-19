from flask import Blueprint, abort, redirect, url_for, \
    render_template, request
from flask.ext.login import current_user
from viaduct.api.mollie import MollieAPI
from viaduct.api.group import GroupPermissionAPI
from viaduct.api.custom_form import CustomFormAPI
import requests

from viaduct import application, db

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')


@blueprint.route('/create', methods=['GET', 'POST'])
def create_mollie_transaction():
    if not GroupPermissionAPI.can_write('mollie'):
        return abort(403)
    redirectUrl, transaction = MollieAPI.create_transaction(
        23.9, 'Een mooie transactie')
    return redirect(redirectUrl)


@blueprint.route('/check')
@blueprint.route('/check/<transaction_id>', methods=['GET', 'POST'])
def mollie_check(trans_id=0):
    success, message = MollieAPI.check_transaction(transaction_id=trans_id)
    CustomFormAPI.update_payment(trans_id, success)

    return render_template('mollie/success.htm', message=message)


@blueprint.route('/webhook', methods=['POST'])
def webhook():
    mollie_id = request.form['id']
    success, message = MollieAPI.check_transaction(mollie_id=mollie_id)
    return render_template('mollie/success.htm', message=message)


@blueprint.route('/')
@blueprint.route('/view/')
def view_all_transactions():
    if not GroupPermissionAPI.can_read('mollie'):
        return abort(403)
    transactions = MollieAPI.get_all_transactions()
    return render_template('mollie/view.htm', transactions=transactions)
