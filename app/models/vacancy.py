from app import db
from datetime import datetime

from app.models.company import Company
from app.models.base_model import BaseEntity


class Vacancy(db.Model, BaseEntity):
    __tablename__ = 'vacancy'

    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    contract_of_service = db.Column(
        db.Enum('voltijd', 'deeltijd', 'bijbaan', 'stage',
                name='vacancy_type'))
    workload = db.Column(db.String(256))
    date = db.Column(db.DateTime)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    company = db.relationship(Company, backref=db.backref('vacancies',
                              lazy='dynamic'))

    def __init__(self, title='', description='', start_date=None,
                 end_date=None, contract_of_service=None, workload='',
                 company=None):
        self.title = title
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.contract_of_service = contract_of_service
        self.workload = workload
        self.date = datetime.now()
        self.company = company

    @property
    def expired(self):
        return self.start_date < datetime.date(datetime.utcnow()) and \
            self.end_date < datetime.date(datetime.utcnow())
