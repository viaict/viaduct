from app import db
from app.models.location import Location
from app.models.contact import Contact
from app.models import BaseEntity


class Company(db.Model, BaseEntity):
    __tablename__ = 'company'

    name = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(1024))
    logo_path = db.Column(db.String(256))
    website = db.Column(db.String(256))
    contract_start_date = db.Column(db.Date)
    contract_end_date = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    rank = db.Column(db.Integer)
    location = db.relationship(Location, backref=db.backref('companies',
                               lazy='dynamic'))
    contact = db.relationship(Contact, backref=db.backref('companies',
                              lazy='dynamic'))

    def __init__(self, name='', description='', contract_start_date=None,
                 contract_end_date=None, location=None, contact=None,
                 website=None, rank=1000, logo_path='#'):
        self.name = name
        self.description = description
        self.contract_start_date = contract_start_date
        self.contract_end_date = contract_end_date
        self.location = location
        self.contact = contact
        self.website = website
        self.logo_path = logo_path
        self.rank = rank
