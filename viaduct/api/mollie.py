import Mollie
from flask.ext.login import current_user
from flask import abort
from viaduct.models.mollie import Transaction


from viaduct import db, application

MOLLIE = Mollie.API.Client()
MOLLIE_URL = application.config['MOLLIE_URL']
MOLLIE_REDIRECT_URL = application.config['MOLLIE_REDIRECT_URL']
MOLLIE_TEST_MODE = application.config.get('MOLLIE_TEST_MODE', False)
if MOLLIE_TEST_MODE:
    MOLLIE.setApiKey(application.config['MOLLIE_TEST_KEY'])
    print 'USING MOLLIE TEST KEY'
else:
    MOLLIE.setApiKey(application.config['MOLLIE_KEY'])
    print 'USING MOLLIE LIVE KEY'


class MollieAPI:
    @staticmethod
    def create_transaction(amount, description, user=current_user,
                           form_result=None):
        # Only create a new transaction is there is a related form result
        if form_result:
            transaction = Transaction()
            transaction.form_result = form_result
        else:
            return False

        # Commit transaction to the database so it gets an ID
        db.session.add(transaction)
        db.session.commit()

        # Add transaction costs
        amount += 1.20

        # Create the mollie payment
        try:
            payment = MOLLIE.payments.create({
                'amount': amount,
                'description': description,
                'redirectUrl': MOLLIE_REDIRECT_URL,
                'metadata': {
                    'transaction_id': transaction.id,
                    'first_name': form_result.owner.first_name,
                    'last_name': form_result.owner.first_last
                }
            })

            transaction.status = payment['status']

            transaction.mollie_id = payment['id']

            db.session.add(transaction)
            db.session.commit()

            return payment.getPaymentUrl(), transaction

        except Mollie.API.Error as e:
            return False, 'API call failed: ' + e.message

    @staticmethod
    def get_payment_url(transaction_id=0, mollie_id=""):
        if not (transaction_id or mollie_id):
            return False, 'no id given'
        if transaction_id and not mollie_id:
            transaction = Transaction.query.\
                filter(Transaction.id == transaction_id).first()
            mollie_id = transaction.mollie_id

        try:
            payment = MOLLIE.payments.get(mollie_id)

            return payment.getPaymentUrl(), ''
        except Mollie.API.Error as e:
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

            if payment.isPaid():
                return True, 'De transactie is afgerond.'
            elif payment.isPending():
                return False, 'De transactie is nog bezig.'
            elif payment.isOpen():
                return False, 'De transactie is nog niet begonnen.'
            return False, 'De transactie is afgebroken.'
        except Mollie.API.Error as e:
            return False, 'API call failed: ' + e.message

    @staticmethod
    def get_all_transactions():
        try:
            payments = MOLLIE.payments.all()
            return payments, 'Success'
        except Mollie.API.Error as e:
            return False, 'API call failed: ' + e.message

    # Switches from local to remote ID, or the other way around.
    # Returns local ID if both are given. (should never happen)
    @staticmethod
    def get_other_id(trans_id=None, mollie_id=None):
        if trans_id:
            trans = Transaction.query.\
                filter(Transaction.id == trans_id).first()
            return trans.mollie_id

        if mollie_id:
            trans = Transaction.query.\
                filter(Transaction.mollie_id == mollie_id).first()
            return trans.id
        return None
