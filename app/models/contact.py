from app import db
from app.models.base_model import BaseEntity


class Contact(db.Model, BaseEntity):
    __tablename__ = 'contact'

    name = db.Column(db.String(256))
    email = db.Column(db.String(200), unique=True)
    phone_nr = db.Column(db.String(64))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    location = db.relationship('Location',
                               backref=db.backref('contacts', lazy='dynamic'))
