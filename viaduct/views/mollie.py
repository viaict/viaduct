from flask import Blueprint, abort, render_template, request
from viaduct.api.mollie import MollieAPI
from viaduct.api.group import GroupPermissionAPI
from viaduct.api.custom_form import CustomFormAPI
from viaduct import application

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')


@blueprint.route('/check')
@blueprint.route('/check/<trans_id>', methods=['GET', 'POST'])
def mollie_check(trans_id=0):
    if ('id' not in request.form) and (not trans_id):
        return render_template('mollie/success.htm', message='no ids given')

    mollie_id = 0
    if 'id' in request.form:
        mollie_id = request.form['id']

    success, message = MollieAPI.check_transaction(transaction_id=trans_id,
                                                   mollie_id=mollie_id)
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
    transactions, message = MollieAPI.get_all_transactions()
    print(transactions)
    test = application.config.get('MOLLIE_TEST_MODE', False)
    key = application.config.get('MOLLIE_TEST_KEY', False)
    if transactions:
        return render_template('mollie/view.htm', transactions=transactions,
                               test=test, key=key, message=message)
    else:
        return render_template('mollie/success.htm', message=message,
                               test=test, key=key)


@blueprint.route('/remote/')
@blueprint.route('/view/remote/')
def view_all_remote_transactions():
    if not GroupPermissionAPI.can_read('mollie'):
        return abort(403)
    payments, message = MollieAPI.get_all_remote_transactions()
    print(payments)
    test = application.config.get('MOLLIE_TEST_MODE', False)
    key = application.config.get('MOLLIE_TEST_KEY', False)
    if payments:
        return render_template('mollie/view.htm', payments=payments)
    else:
        return render_template('mollie/success.htm', message=message)
