# coding=utf-8
from app import app
from app.models import User

from flask_wtf import Form
from flask_wtf.recaptcha import RecaptchaField, Recaptcha
from wtforms import StringField, PasswordField, BooleanField, \
    SelectField, IntegerField, FileField
from wtforms.widgets import TextInput
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError,\
    Length, Optional

from flask_babel import lazy_gettext as _, gettext  # noqa

import dateutil
import bcrypt

_min_password_length = app.config['MIN_PASSWORD_LENGTH']


class DateField(StringField):
    widget = TextInput()

    def _value(self):
        if self.data:
            return self.data.strftime('%d-%m-%Y')

        return ''

    def process_formdata(self, valuelist):
        if valuelist:
            v = ' '.join(valuelist)

            if v:
                self.data = dateutil.parser.parse(v, dayfirst=True).date()
                return

        self.data = None


class BaseUserForm(Form):
    email = StringField(_('E-mail adress'), validators=[
        InputRequired(message=_('No e-mail adress submitted')),
        Email(message=_('Invalid e-mail adress submitted'))])
    first_name = StringField(_('First name'), validators=[
        InputRequired(message=_('No first name sunmitted'))]
    )
    last_name = StringField(_('Last name'), validators=[
        InputRequired(message=_('No last name submitted'))]
    )
    student_id = StringField(_('Student ID'), validators=[
        InputRequired(message=_('No studentnumber submitted'))]
    )
    education_id = SelectField(_('Education'), coerce=int)
    receive_information = BooleanField(_('Would you like to recieve '
                                         'information from companies?'))

    address = StringField(_('Address'))
    zip = StringField(_('Zip code'))
    city = StringField(_('City'))
    country = StringField(_('Country'), default='Nederland')

    # Dates
    birth_date = DateField(_('Birthdate'), validators=[
        InputRequired(message=_('No birthdate submitted'))])
    study_start = DateField(_('Starting year study'), validators=[
        InputRequired(message=_('No starting year of study submitted'))])

    # Optional fields
    locale = SelectField(_('Language'), validators=[
        Optional()], choices=list(app.config['LANGUAGES'].items()))
    phone_nr = StringField(_('Phone'), validators=[Optional()])
    avatar = FileField('Avatar', validators=[Optional()])


class SignUpForm(BaseUserForm):
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(message=_('No password submitted')),
            Length(message=(_('Minimal password length ') +
                            str(_min_password_length)),
                   min=_min_password_length)]
    )
    repeat_password = PasswordField(
        _('Repeat password'), validators=[
            InputRequired(message=_('Passwords do not match')),
            EqualTo('password', message=_('Passwords do not match'))]
    )
    birth_date = DateField(_('Birthdate'), validators=[
        InputRequired(message=_('No birthdate submitted'))])
    study_start = DateField(_('Starting year study'), validators=[
        InputRequired(message=_('No starting year of study submitted'))])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message='Check Recaptcha')])


class EditUserForm(BaseUserForm):
    """Edit a user as administrator."""

    id = IntegerField('ID')
    password = PasswordField(_('Password'))
    repeat_password = PasswordField(_('Repeat password'))
    has_payed = BooleanField(_('Has payed'))
    honorary_member = BooleanField(_('Honorary member'))
    favourer = BooleanField(_('Favourer'))
    disabled = BooleanField(_('Disabled'))
    alumnus = BooleanField(_('Alumnus'))

    def validate_password(self, field):
        """Providing a password is only required when creating a new user."""
        if self.id.data == 0 and len(field.data) == 0:
            raise ValidationError(_('No password submitted'))

    def validate_repeat_password(self, field):
        """Only validate the repeat password if a password is set."""
        if len(self.password.data) > 0 and field.data != self.password.data:
            raise ValidationError(_('Passwords do not match'))


class EditUserInfoForm(BaseUserForm):
    """Edit your own user information."""

    id = IntegerField('ID')
    password = PasswordField(
        _('Password'), validators=[
            Length(message=(_('Minimal password length ') +
                            str(_min_password_length)),
                   min=_min_password_length),
            Optional()]
    )
    repeat_password = PasswordField(
        _('Repeat password'), validators=[
            EqualTo('password', message=_('Passwords do not match'))]
    )

    def validate_password(self, field):
        """Providing a password is only required when creating a new user."""
        if self.id.data == 0 and len(field.data) == 0:
            raise ValidationError(_('No password submitted'))

    def validate_repeat_password(self, field):
        """Only validate the repeat password if a password is set."""
        if len(self.password.data) > 0 and field.data != self.password.data:
            raise ValidationError(_('Passwords do not match'))


class SignInForm(Form):
    email = StringField(_('E-mail adress'), validators=[
        InputRequired(message=_('No e-mail adress submitted')),
        Email(message=_('Invalid e-mail adress submitted'))])
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(message=_('No password submitted'))])

    def validate_signin(self):
        user = User.query.filter(User.email == self.email.data.strip()).first()

        if self._errors is None:
            self._errors = dict()

        if user is None:
            self._errors['email'] = [_(
                'It appears that account does not exist. Try again, or contact'
                ' the website administration at ict (at) svia (dot) nl.')]
            return None

        submitted_hash = bcrypt.hashpw(self.password.data, user.password)
        if submitted_hash != user.password:
            self._errors['password'] = [_(
                'The password you entered appears to be incorrect.')]
            return None

        return user


class RequestPassword(Form):
    email = StringField(_('E-mail adress'), validators=[
        InputRequired(message=_('No e-mail adress submitted')),
        Email(message=_('Invalid e-mail adress submitted'))])
    student_id = StringField(
        _('Student ID'), validators=[
            InputRequired(message=_('No studentnumber submitted'))]
    )


class ResetPassword(Form):
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(message=_('No password submitted')),
            Length(message=(_('Minimal password length ') +
                            str(_min_password_length)),
                   min=_min_password_length)]
    )
    password_repeat = PasswordField(
        _('Repeat password'), validators=[
            InputRequired(message=_('Passwords do not match')),
            EqualTo('password', message=_('Passwords do not match'))]
    )
