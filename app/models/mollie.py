from viaduct import db
from viaduct.models import BaseEntity


class Transaction(db.Model, BaseEntity):
    __tablename__ = 'mollie_transaction'

    mollie_id = db.Column(db.String(256))
    status = db.Column(
        db.Enum('open', 'cancelled', 'paidout', 'paid', 'expired'))
    form_result_id = db.Column(db.Integer,
                               db.ForeignKey('custom_form_result.id'))

    form_result = db.relationship('CustomFormResult',
                                  backref=db.backref('mollie_transaction',
                                                     lazy='dynamic'))

    def __init__(self, status='open', form_result_id=0):
        self.status = status
        self.form_result_id = form_result_id
