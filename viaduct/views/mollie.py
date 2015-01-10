from flask import Blueprint, abort, render_template, request
from viaduct import application
from viaduct.api.mollie import MollieAPI
from viaduct.api.group import GroupPermissionAPI
from viaduct.api.custom_form import CustomFormAPI

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')


@blueprint.route('/check')
@blueprint.route('/check/<trans_id>', methods=['GET', 'POST'])
def mollie_check(trans_id=0):
    if ('id' not in request.form) and (not trans_id):
        return render_template('mollie/success.htm', message='no ids given')
    if trans_id:
        mollie_id = MollieAPI.get_other_id(trans_id=trans_id)
    elif 'id' in request.form:
        mollie_id = request.form['id']
        trans_id = MollieAPI.get_other_id(mollie_id=mollie_id)

    success, message = MollieAPI.check_transaction(transaction_id=trans_id,
                                                   mollie_id=mollie_id)
    CustomFormAPI.update_payment(trans_id, success)

    return render_template('mollie/success.htm', message=message)


@blueprint.route('/webhook/', methods=['POST'])
def webhook():
    if 'id' not in request.form:
        return 'Message received without ID'
    mollie_id = request.form['id']
    success, message = MollieAPI.check_transaction(mollie_id=mollie_id)
    trans_id = MollieAPI.get_other_id(mollie_id=mollie_id)
    CustomFormAPI.update_payment(trans_id, success)
    return 'Message received'


@blueprint.route('/')
@blueprint.route('/view/')
def view_all_transactions():
    if not GroupPermissionAPI.can_read('mollie'):
        return abort(403)
    payments, message = MollieAPI.get_all_transactions()
    test = application.config.get('MOLLIE_TEST_MODE', False)
    if payments:
        return render_template('mollie/view.htm', payments=payments,
                               test=test)
    else:
        return render_template('mollie/success.htm', message=message,
                               test=test)
