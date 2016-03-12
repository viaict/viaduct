from app.models.mollie import Transaction
from app import db


class CustomFormAPI:
    @staticmethod
    def update_payment(transaction_id, payed):
        transaction = Transaction.query.filter(
            Transaction.id == transaction_id).first()
        if transaction.form_result:
            transaction.form_result.has_payed = payed
            db.session.commit()
        return
