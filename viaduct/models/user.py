from viaduct import db
from viaduct.models.education import Education
from datetime import datetime
from viaduct.models import BaseEntity
from config import LANGUAGES


class User(db.Model, BaseEntity):
    __tablename__ = 'user'

    prints = ('id', 'email', 'password', 'first_name', 'last_name',
              'student_id')

    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(60))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    locale = db.Column(db.Enum(*LANGUAGES.keys()), default="nl")
    has_payed = db.Column(db.Boolean, default=None)
    shirt_size = db.Column(db.Enum('Small', 'Medium', 'Large'))
    allergy = db.Column(db.String(1024))  # Allergy / medication
    diet = db.Column(db.Enum('Vegetarisch', 'Veganistisch', 'Fruitarier'))
    gender = db.Column(db.Enum('Man', 'Vrouw', 'Geen info'))
    phone_nr = db.Column(db.String(16))
    emergency_phone_nr = db.Column(db.String(16))
    description = db.Column(db.String(1024))  # Description of user
    student_id = db.Column(db.String(256))
    education_id = db.Column(db.Integer, db.ForeignKey('education.id'))
    created = db.Column(db.DateTime, default=datetime.now())
    honorary_member = db.Column(db.Boolean, default=False)
    favourer = db.Column(db.Boolean, default=False)
    payed_date = db.Column(db.DateTime)
    birth_date = db.Column(db.Date)
    study_start = db.Column(db.Date)

    education = db.relationship(Education,
                                backref=db.backref('user', lazy='dynamic'))

    def __init__(self, email=None, password=None, first_name=None,
                 last_name=None, student_id=None, education_id=None,
                 birth_date=None, study_start=None):
        if not email:
            self.id = 0

        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.student_id = student_id
        self.education_id = education_id

        self.birth_date = birth_date
        self.study_start = study_start

    def __setattr__(self, name, value):
        """ if has_payed is set to true, we want to store the date that
        happend.  Because of legacy code and sqlalchemy we do it this way """
        if name == 'has_payed' and value:
            super(User, self).__setattr__("payed_date", datetime.now())
        super(User, self).__setattr__(name, value)

    def is_authenticated(self):
        """Necessary."""
        return self.id != 0

    def is_active(self):
        """Necessary."""
        return self.id != 0

    def is_anonymous(self):
        return self.id == 0

    def get_id(self):
        """Necessary for Flask-Login."""
        return str(self.id)

    @property
    def name(self):
        """The user's name."""
        return ' '.join([self.first_name, self.last_name])

    @staticmethod
    def get_anonymous_user():
        return User.query.get(0)
