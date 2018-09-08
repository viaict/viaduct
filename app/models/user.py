from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin

from app import db, constants
from app.models.base_model import BaseEntity
from app.models.education import Education
from app.service import group_service


class AnonymousUser(AnonymousUserMixin):
    """
    Has attributes for flask-login.

    is_anonymous = True, is_active & is_authenticated = False.
    current_user is equal to an instance of this class whenever the user is
    not logged in.

    Check logged in using:
    >>> from flask_login import login_required
    >>> from flask import Blueprint
    >>>
    >>> blueprint = Blueprint("somemodule", __name__)
    >>> @blueprint.route("/someroute")
    >>> @login_required

    Keep in mind, all the user attributes are not available when the user is
    not logged in.
    """

    id = 0
    has_paid = False
    groups = []


class User(db.Model, UserMixin, BaseEntity):
    """The groups property is backreferenced from group.py."""

    __tablename__ = 'user'

    prints = ('id', 'email', 'password', 'first_name', 'last_name',
              'student_id', 'receive_information')

    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(60))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    locale = db.Column(db.Enum(*list(constants.LANGUAGES.keys()),
                               name='locale'),
                       default="nl")
    has_paid = db.Column(db.Boolean, default=None)
    shirt_size = db.Column(db.Enum('Small', 'Medium', 'Large',
                                   name='user_shirt_size'))
    allergy = db.Column(db.String(1024))  # Allergy / medication
    diet = db.Column(db.Enum('Vegetarisch', 'Veganistisch', 'Fruitarier',
                             name='user_diet'))
    gender = db.Column(db.Enum('Man', 'Vrouw', 'Geen info',
                               name='user_sex'))
    phone_nr = db.Column(db.String(16))
    emergency_phone_nr = db.Column(db.String(16))
    description = db.Column(db.String(1024))  # Description of user
    student_id = db.Column(db.String(256))
    education_id = db.Column(db.Integer, db.ForeignKey('education.id'))
    created = db.Column(db.DateTime, default=datetime.now)
    honorary_member = db.Column(db.Boolean, default=False)
    favourer = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    birth_date = db.Column(db.Date)
    study_start = db.Column(db.Date)
    receive_information = db.Column(db.Boolean, default=False)
    disabled = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(256))
    zip = db.Column(db.String(8))
    city = db.Column(db.String(256))
    country = db.Column(db.String(256), default='Nederland')
    alumnus = db.Column(db.Boolean, default=False)
    education = db.relationship(Education,
                                backref=db.backref('user', lazy='dynamic'))
    copernica_id = db.Column(db.Integer(), nullable=True)
    avatar_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))

    student_id_confirmed = db.Column(db.Boolean, default=False, nullable=False)

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
        If has_paid is set to true, we want to store the date that happend.

        Because of legacy code and sqlalchemy we do it this way
        """
        if name == 'has_paid' and value:
            super(User, self).__setattr__(
                "paid_date", datetime.now())

        super(User, self).__setattr__(name, value)

    def __str__(self):
        return self.name

    def get_user_id(self):
        """Retrieve the unique id of the user for authlib."""
        return self.id

    def update_email(self, new_email):
        if self.email == new_email:
            return

        old_email = self.email

        for group in self.groups:
            if not group.maillist:
                continue

            group.remove_email_from_maillist(old_email)
            group.add_email_to_maillist(new_email)

        self.email = new_email

    def member_of_group(self, group_id: int) -> bool:
        group = group_service.find_group_by_id(group_id)
        if group:
            return group.has_user(self)
        return False

    @property
    def name(self):
        if not self.first_name and not self.last_name:
            return None
        return ' '.join([self.first_name, self.last_name])
