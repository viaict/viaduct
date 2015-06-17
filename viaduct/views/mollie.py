from flask import Blueprint, abort, render_template, request, url_for
from viaduct import application
from viaduct.api.mollie import MollieAPI
from viaduct.api.module import ModuleAPI
from viaduct.api.custom_form import CustomFormAPI
from viaduct.models.mollie import Transaction
from viaduct.models.activity import Activity

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')


@blueprint.route('/check')
@blueprint.route('/check/<trans_id>', methods=['GET', 'POST'])
def mollie_check(trans_id=0, mollie_id=0):
    if not trans_id:
        if 'id' not in request.form:
            return render_template('mollie/success.htm', message='no id given')
        else:
            mollie_id = request.form['id']
            trans_id = MollieAPI.get_other_id(mollie_id=mollie_id)

    transaction = Transaction.query.\
        filter(Transaction.id == trans_id).first()
    if not transaction:
        return render_template('mollie/success.htm',
                               message='unknown transaction')
    form_id = transaction.form_result.form.id
    activity = Activity.query.\
        filter(Activity.form_id == form_id).first()
    if activity:
        link = url_for('activity.get_activity', activity_id=activity.id)
    else:
        link = False
    success, message = MollieAPI.check_transaction(transaction_id=trans_id,
                                                   mollie_id=mollie_id)
    CustomFormAPI.update_payment(trans_id, success)
    return render_template('mollie/success.htm',
                           message=message,
                           link=link)


@blueprint.route('/webhook/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return ''
    if 'id' not in request.form:
        return ''
    mollie_id = request.form['id']
    success, message = MollieAPI.check_transaction(mollie_id=mollie_id)
    trans_id = MollieAPI.get_other_id(mollie_id=mollie_id)
    CustomFormAPI.update_payment(trans_id, success)
    return ''


@blueprint.route('/')
@blueprint.route('/view/')
@blueprint.route('/view/<int:page>')
def view_all_transactions(page=0):
    if not ModuleAPI.can_read('mollie'):
        return abort(403)

    test = application.config.get('MOLLIE_TEST_MODE', False)
    key = application.config.get('MOLLIE_TEST_KEY', False)
    print(key)

    payments, message = MollieAPI.get_transactions(page)
    print(payments)
    print(message)
    if payments:
        return render_template('mollie/view.htm', payments=payments,
                               test=test, key=key, message=message, page=page)
    else:
        return render_template('mollie/success.htm', message=message,
                               test=test, key=key)
