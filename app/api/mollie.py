from flask.ext.login import current_user
from flask import abort, url_for
from app.models.mollie import Transaction


from app import db, app

import mollie.api.error as mollie_error
from mollie.api.client import Client

MOLLIE = Client()
MOLLIE_TEST_MODE = app.config.get('MOLLIE_TEST_MODE', False)
if MOLLIE_TEST_MODE:
    MOLLIE.set_api_key(app.config['MOLLIE_TEST_KEY'])
    print('USING MOLLIE TEST KEY')
else:
    MOLLIE.set_api_key(app.config['MOLLIE_KEY'])
    print('USING MOLLIE LIVE KEY')


class MollieAPI:
    @staticmethod
    def create_transaction(amount, description, user=current_user,
                           form_result=None):
        # Only create a new transaction if there is a related form result
        if form_result:
            transaction = Transaction()
            transaction.form_result = form_result
        else:
            return False

        # Commit transaction to the database so it gets an ID
        db.session.add(transaction)
        db.session.commit()

        # Add transaction costs
        amount += 0.50

        # Create the mollie payment
        try:
            payment = MOLLIE.payments.create({
                'amount': amount,
                'description': description,
                'redirectUrl': url_for('mollie.mollie_check',
                                       trans_id=transaction.id,
                                       _external=True),
                'metadata': {
                    'transaction_id': transaction.id,
                    'first_name': form_result.owner.first_name,
                    'last_name': form_result.owner.last_name,
                    'form_name': form_result.form.name
                }
            })

            transaction.status = payment['status']

            transaction.mollie_id = payment['id']

            db.session.add(transaction)
            db.session.commit()

            return payment.get_payment_url(), transaction

        except mollie_error.Error as e:
            return False, 'API call failed: ' + e.message

    @staticmethod
    def get_payment_url(transaction_id=0, mollie_id=""):
        if not (transaction_id or mollie_id):
            return False, 'no id given'
        if transaction_id and not mollie_id:
            mollie_id = MollieAPI.get_other_id(transaction_id)

        try:
            payment = MOLLIE.payments.get(mollie_id)

            return payment.get_payment_url(), ''
        except mollie_error.Error as e:
            return False, 'API call failed: ' + e.message

    @staticmethod
    def check_transaction(transaction_id=0, mollie_id=""):
        if transaction_id:
            transaction = Transaction.query.\
                filter(Transaction.id == transaction_id).first()
        else:
            transaction = Transaction.query.\
                filter(Transaction.mollie_id == mollie_id).first()

        if not transaction:
            abort(404)

        try:
            payment = MOLLIE.payments.get(transaction.mollie_id)

            transaction.status = payment['status']

            db.session.commit()

            if payment.is_paid():
                return True, 'De transactie is afgerond.'
            elif payment.is_pending():
                return False, 'De transactie is nog bezig.'
            elif payment.is_open():
                return False, 'De transactie is nog niet begonnen.'
            return False, 'De transactie is afgebroken.'
        except mollie_error.Error as e:
            return False, 'API call failed: ' + e.message

    @staticmethod
    def get_transactions(page=0):
        try:
            payments = MOLLIE.payments.all(offset=page*20, count=20)[0]
        except mollie_error.Error as e:
            return False, 'Api call failed: ' + e.message

        for payment in payments['data']:
            transaction = Transaction.query.\
                filter(Transaction.mollie_id == payment['id']).first()
            if not isinstance(payment['metadata'], dict):
                payment['metadata'] = {}
            if 'first_name' not in payment['metadata']:
                if transaction:
                    payment['metadata']['first_name'] =\
                        transaction.form_result.owner.first_name
                    payment['metadata']['last_name'] =\
                        transaction.form_result.owner.last_name
            if 'form_name' not in payment['metadata']:
                if transaction:
                    payment['metadata']['form_name'] =\
                        transaction.form_result.form.name

        return payments, 'success'

    @staticmethod
    def get_all_remote_transactions():
        try:
            payments = MOLLIE.payments.all()
            return payments, 'Success'
        except mollie_error.Error as e:
            return False, 'API call failed: ' + e.message

    # Switches from local to remote ID, or the other way around.
    # Returns local ID if both are given. (should never happen)
    @staticmethod
    def get_other_id(trans_id=None, mollie_id=None):
        if trans_id:
            trans = Transaction.query.\
                filter(Transaction.id == trans_id).first()
            if trans:
                return trans.mollie_id

        if mollie_id:
            trans = Transaction.query.\
                filter(Transaction.mollie_id == mollie_id).first()
            if trans:
                return trans.id
        return None
