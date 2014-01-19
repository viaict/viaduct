from viaduct import db


class Contact(db.Model):
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True)
    phone_nr = db.Column(db.String(64))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    location = db.relationship('Location',
                               backref=db.backref('contacts', lazy='dynamic'))

    def __init__(self, name='', email='', phone_nr='', location=None):
        self.name = name
        self.email = email
        self.phone_nr = phone_nr
        self.location = location
