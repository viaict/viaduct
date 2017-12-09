from flask import (Blueprint, abort, render_template, request, url_for, flash,
                   redirect)
from mollie.api.error import Error as MollieError

from app import db
from app.decorators import require_role
from app.models.mollie import Transaction
from app.roles import Roles
from app.utils import mollie
from app.utils.mollie import MollieClient, check_transaction

blueprint = Blueprint('mollie', __name__, url_prefix='/mollie')


@blueprint.route('/return/')
@blueprint.route('/return/<int:transaction_id>/', methods=['GET'])
def callback(transaction_id=None):
    transaction = Transaction.query.get_or_404(transaction_id)
    (_, message) = check_transaction(transaction)
    return render_template('mollie/success.htm', message=message)


@blueprint.route('/check/', methods=['GET', 'POST'])
@blueprint.route('/check/<mollie_id>/', methods=['GET', 'POST'])
@blueprint.route('/check/transaction/<int:transaction_id>/',
                 methods=['GET', 'POST'])
def check(mollie_id=None, transaction_id=None):

    if transaction_id:
        transaction = Transaction.query.filter(
            Transaction.id == transaction_id).first() or abort(404)
    elif mollie_id:
        transaction = Transaction.query.filter(
            Transaction.mollie_id == mollie_id).first() or abort(404)
    else:
        abort(404)

    (success, msg) = check_transaction(transaction)
    flash(msg, 'success') if success else flash(msg, 'danger')
    return redirect(url_for('mollie.list'))


@blueprint.route('/webhook/', methods=['POST'])
def webhook():
    try:
        payment_id = request.form.get('id', None)
        transaction = Transaction.query.filter(
            Transaction.mollie_id == payment_id).first()

        if not transaction:
            raise MollieError('Transaction cannot be found')

        payment = MollieClient.payments.get(payment_id)
        transaction.status = payment['status']
        db.session.commit()

        if payment.is_paid():
            transaction.process_callbacks()
        return '', 200
    except MollieError:
        if request.args.get('testByMollie') == 1:
            return 'Mollie check error: no id', 200
        return '', 404


@blueprint.route('/')
@blueprint.route('/<int:page>/')
@require_role(Roles.MOLLIE_READ)
def list(page=0):
    payments, message = mollie.get_payments(page)
    return render_template('mollie/list.htm', payments=payments,
                           message=message, page=page)
