from app import db
from app.models.base_model import BaseEntity
from app.models.contact import Contact
from app.models.location import Location


class Company(db.Model, BaseEntity):
    __tablename__ = 'company'

    name = db.Column(db.String(200), unique=True)
    description = db.Column(db.String(1024))
    logo_file_id = db.Column(db.Integer, db.ForeignKey('file.id'),
                             nullable=True)
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

    expired: bool
