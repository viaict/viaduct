from functools import wraps

from app import db, app
from app.models.mollie import Transaction

from flask import url_for
from flask_login import current_user

from flask_babel import _

from mollie.api.client import Client
from mollie.api.error import Error as MollieError

import itertools
import logging

_logger = logging.getLogger(__name__)

MollieClient = Client()


def init_mollie(f):
    """Lazy initialization of the mollie client."""

    @wraps
    def wrapped(*args, **kwargs):
        if app.config['MOLLIE_KEY']:
            MollieClient.set_api_key(app.config['MOLLIE_KEY'])
            _logger.info('Using MOLLIE_KEY: %s', app.config['MOLLIE_KEY'])
        else:
            _logger.info('Using MOLLIE_KEY: NOTSET')
        return f(args, kwargs)

    return wrapped


@init_mollie
def create_transaction(amount, description, user=current_user,
                       callbacks=list()):
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

    # Create the mollie payment
    try:
        payment = MollieClient.payments.create({
            'amount': amount,
            'description': "{}, {}".format(user.name, description),
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


@init_mollie
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
            return None, _('Your payment has status: %s' % status)
    except MollieError as e:
        return None, _('API call failed: %s' % e.message)


@init_mollie
def get_payments(page=0):
    try:
        payments = MollieClient.payments.all(offset=page * 20, count=20)[0]
        return payments['data'], 'success'
    except MollieError as e:
        return [], _('Api call failed: %s' % e.message)
