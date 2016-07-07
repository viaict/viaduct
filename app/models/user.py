from app import db, app
from app.models import BaseEntity, Group
from app.models.education import Education
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime


class AnonymousUser(AnonymousUserMixin):
    """
    Has attributes for flask-login.

    is_anonymous = True, is_active & is_authenticated = False.
    current_user is equal to an instance of this class whenever the user is
    not logged in.

    Check logged in using:

    >>> if current_user.is_anonymous:
    >>>     abort(403)

    Keep in mind, all the user attributes are not available when the user is
    not logged in.
    """

    id = 0
    has_payed = False


class User(db.Model, UserMixin, BaseEntity):
    __tablename__ = 'user'

    prints = ('id', 'email', 'password', 'first_name', 'last_name',
              'student_id', 'receive_information')

    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(60))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    locale = db.Column(db.Enum(*list(app.config['LANGUAGES'].keys())),
                       default="nl")
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
    receive_information = db.Column(db.Boolean, default=False)
    disabled = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(256))
    zip = db.Column(db.String(8))
    city = db.Column(db.String(256))
    country = db.Column(db.String(256), default='Nederland')

    education = db.relationship(Education,
                                backref=db.backref('user', lazy='dynamic'))

    def __init__(self, email=None, password=None, first_name=None,
                 last_name=None, student_id=None, education_id=None,
                 birth_date=None, study_start=None, receive_information=None):
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
        self.receive_information = receive_information

    def __setattr__(self, name, value):
        """
        If has_payed is set to true, we want to store the date that happend.

        Because of legacy code and sqlalchemy we do it this way
        """
        if name == 'has_payed' and value:
            super(User, self).__setattr__("payed_date", datetime.now())
        super(User, self).__setattr__(name, value)

    def update_email(self, new_email):
        if self.email == new_email:
            return

        old_email = self.email

        groups_with_email = self.groups.filter(
            Group.maillist != None,
            Group.maillist != '').all()  # noqa

        for group in groups_with_email:
            group.remove_email_from_maillist(old_email)
            group.add_email_to_maillist(new_email)

        self.email = new_email

    @property
    def name(self):
        """The user's name."""
        if not self.first_name and not self.last_name:
            return None
        return ' '.join([self.first_name, self.last_name])

    @staticmethod
    def get_anonymous_user():
        return User.query.get(0)
