from app import db, app
from app.models.mollie import Transaction

from flask import url_for
from flask_login import current_user

from flask_babel import _

from mollie.api.client import Client
from mollie.api.error import Error as MollieError

import itertools

MollieClient = Client()

if app.config.get('MOLLIE_TEST_MODE', False):
    MollieClient.set_api_key(app.config['MOLLIE_TEST_KEY'])
    print('USING MOLLIE TEST KEY')
else:
    MollieClient.set_api_key(app.config['MOLLIE_KEY'])
    print('USING MOLLIE LIVE KEY')


def create_transaction(amount, description, user=current_user,
                       callbacks=[]):

    # Only create a new transaction if there is a related form result
    if not isinstance(callbacks, list):
        callbacks = [callbacks]
    callbacks.sort(key=lambda cb: cb.__class__.__name__)

    # Commit transaction to the database so it gets an ID
    transaction = Transaction()
    db.session.add(transaction)
    db.session.commit()

    for cb in callbacks:
        cb.transaction = transaction
    db.session.commit()

    # Add transaction costs
    amount += 0.35

    # Create the mollie payment
    try:
        payment = MollieClient.payments.create({
            'amount': amount,
            'description': description if description else 'VIA Transaction',
            'redirectUrl': url_for('mollie.callback',
                                   transaction_id=transaction.id,
                                   _external=True),
            'metadata': {
                'transaction_id': transaction.id,
                'user_id': user.id,
                'user_email': user.email,
                'callbacks': {
                    k: [cb.id for cb in v] for k, v in
                    itertools.groupby(callbacks,
                                      key=lambda x: x.__class__.__name__)
                }
            }
        })

        transaction.status = payment['status']
        transaction.mollie_id = payment['id']
        db.session.add(transaction)
        db.session.commit()

        return payment.get_payment_url(), transaction

    except MollieError as e:
        return False, _('API call failed: %s' % e.message)


def check_transaction(transaction):
    try:
        payment = MollieClient.payments.get(transaction.mollie_id)
        transaction.status = payment['status']
        db.session.commit()

        if payment.is_paid():
            transaction.process_callbacks()
            return payment, _('Payment successfully received.')
        elif payment.is_pending():
            return payment, _('Your payment is being processed.')
        elif payment.is_open():
            return payment, _('Your payment has not been completed.')
        else:
            status = payment['status']
            return False, _('Your payment has status: %s' % status)
    except MollieError as e:
        return False, _('API call failed: %s' % e.message)


def get_payments(page=0):
    try:
        payments = MollieClient.payments.all(offset=page * 20, count=20)[0]
        return payments['data'], 'success'
    except MollieError as e:
        return [], _('Api call failed: %s' % e.message)
