from app import db
from app.models import BaseEntity


class Contact(db.Model, BaseEntity):
    __tablename__ = 'contact'

    name = db.Column(db.String(256))
    email = db.Column(db.String(200), unique=True)
    phone_nr = db.Column(db.String(64))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    location = db.relationship('Location',
                               backref=db.backref('contacts', lazy='dynamic'))

    def __init__(self, name='', email='', phone_nr='', location=None):
        self.name = name
        self.email = email
        self.phone_nr = phone_nr
        self.location = location
