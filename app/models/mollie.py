from app import db
from app.models import BaseEntity
from sqlalchemy.ext.declarative import declared_attr


class Transaction(db.Model, BaseEntity):
    prints = ('id', 'mollie_id', 'status')

    mollie_id = db.Column(db.String(256))
    status = db.Column(
        db.Enum('open', 'cancelled', 'pending', 'expired', 'failed',
                'paid', 'paidout', 'refunded', 'charged_back'),
        nullable=False)

    def __init__(self, status='open'):
        self.status = status

    def process_callbacks(self):
        transaction_products = [cb for cb in dir(self)
                                if cb.startswith('callback_')]

        for product_list in transaction_products:
            products = getattr(self, product_list)
            for product in products:
                product.payment_complete()


class TransactionCallbackMixin(BaseEntity):

    @declared_attr
    def transaction_id(self):
        return db.Column(db.Integer, db.ForeignKey('mollie_transaction.id'))

    def payment_complete():
        """Implement in subclasses that handle wares."""
        raise NotImplementedError()


class TransactionMembership(db.Model, TransactionCallbackMixin):

    user = db.relationship('User')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    transaction = db.relationship("Transaction",
                                  backref=db.backref('callback_membership'))

    def payment_complete(self):
        self.user.has_payed = True
        db.session.commit()


class TransactionActivity(db.Model, TransactionCallbackMixin):

    custom_form_result = db.relationship('CustomFormResult')
    custom_form_result_id = db.Column(db.Integer(),
                                      db.ForeignKey('custom_form_result.id'),
                                      nullable=False)

    transaction = db.relationship("Transaction",
                                  backref=db.backref('callback_activity'))

    def payment_complete(self):
        self.custom_form_result.has_payed = True
        db.session.commit()
