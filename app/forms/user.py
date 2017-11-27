# coding=utf-8
from flask_babel import lazy_gettext as _  # noqa
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField, Recaptcha
from wtforms import StringField, PasswordField, BooleanField, \
    SelectField, FileField, DateField
from wtforms.validators import (InputRequired, EqualTo, ValidationError,
                                Length, Optional)

from app import app
from app.forms.fields import EmailField
from app.forms.util import FieldVerticalSplit

_min_password_length = app.config['MIN_PASSWORD_LENGTH']


class BaseUserForm(FlaskForm):
    email = EmailField(_('E-mail adress'), validators=[InputRequired()])
    first_name = StringField(_('First name'), validators=[InputRequired()])
    last_name = StringField(_('Last name'), validators=[InputRequired()])
    student_id = StringField(_('Student ID'), validators=[InputRequired()])
    education_id = SelectField(_('Education'), coerce=int)
    receive_information = BooleanField(_('Would you like to recieve '
                                         'information from companies?'))

    address = StringField(_('Address'))
    zip = StringField(_('Zip code'))
    city = StringField(_('City'))
    country = StringField(_('Country'), default='Nederland')

    # Dates
    birth_date = DateField(_('Birthdate'), validators=[InputRequired()])
    study_start = DateField(_('Starting year study'),
                            validators=[InputRequired()])

    # Optional fields
    locale = SelectField(_('Language'), validators=[
        Optional()], choices=list(app.config['LANGUAGES'].items()))
    phone_nr = StringField(_('Phone'), validators=[Optional()])
    avatar = FileField('Avatar', validators=[Optional()])


class SignUpForm(BaseUserForm):
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(),
            Length(
                message=(_('Minimal password length: %(length)d',
                           length=_min_password_length)),
                min=_min_password_length)]
    )
    repeat_password = PasswordField(
        _('Repeat password'), validators=[
            InputRequired(),
            EqualTo('password', message=_('Passwords do not match'))]
    )
    birth_date = DateField(_('Birthdate'), validators=[
        InputRequired()])
    study_start = DateField(_('Starting year study'), validators=[
        InputRequired()])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message='Check Recaptcha')])

    register_split = FieldVerticalSplit([
        ['first_name', 'last_name', 'birth_date', 'address', 'zip', 'city',
         'country', 'recaptcha'],
        ['email', 'password', 'repeat_password', 'student_id', 'education_id',
         'study_start', 'receive_information']
    ], large_spacing=True)

    _RenderIgnoreFields = ['locale', 'phone_nr', 'avatar']


class EditUserForm(BaseUserForm):
    """Edit a user as administrator."""

    password = PasswordField(_('Password'))
    repeat_password = PasswordField(_('Repeat password'))
    has_paid = BooleanField(_('Has paid'))
    honorary_member = BooleanField(_('Honorary member'))
    favourer = BooleanField(_('Favourer'))
    disabled = BooleanField(_('Disabled'))

    register_split = FieldVerticalSplit([
        ['first_name', 'last_name', 'birth_date', 'address', 'zip', 'city',
         'country'],
        ['email', 'password', 'repeat_password', 'student_id', 'education_id',
         'study_start', 'receive_information']
    ], large_spacing=True)

    optional_split = FieldVerticalSplit([
        ['phone_nr', 'locale'],
        ['avatar']
    ], large_spacing=True)

    admin_split = FieldVerticalSplit([
        ['has_paid', 'honorary_member'],
        ['favourer', 'disabled']
    ], large_spacing=True)

    alumnus = BooleanField(_('Alumnus'))

    new_user = False

    def validate_password(self, field):
        """Providing a password is only required when creating a new user."""
        if self.new_user:
            if len(field.data) == 0:
                raise ValidationError(_('No password submitted'))
        if len(field.data) > 0 and len(field.data) < _min_password_length:
            raise ValidationError(_('Minimal password length: %(length)d',
                                    length=_min_password_length))

    def validate_repeat_password(self, field):
        """Only validate the repeat password if a password is set."""
        if len(self.password.data) > 0 and field.data != self.password.data:
            raise ValidationError(_('Passwords do not match'))


class EditUserInfoForm(BaseUserForm):
    """Edit your own user information."""

    alumnus = BooleanField(_('Yes, I have finished studying'))

    password = PasswordField(_('Password'))
    repeat_password = PasswordField(_('Repeat password'))

    register_split = FieldVerticalSplit([
        ['first_name', 'last_name', 'birth_date', 'address', 'zip', 'city',
         'country'],
        ['email', 'password', 'repeat_password', 'student_id', 'education_id',
         'study_start']
    ], large_spacing=True)

    optional_split = FieldVerticalSplit([
        ['phone_nr', 'locale'],
        ['avatar']
    ], large_spacing=True)

    new_user = False

    def validate_password(self, field):
        """Providing a password is only required when creating a new user."""
        if self.new_user:
            if len(field.data) == 0:
                raise ValidationError(_('No password submitted'))
        if len(field.data) > 0 and len(field.data) < _min_password_length:
            raise ValidationError(_('Minimal password length: %(length)d',
                                    length=_min_password_length))

    def validate_repeat_password(self, field):
        """Only validate the repeat password if a password is set."""
        if len(self.password.data) > 0 and field.data != self.password.data:
            raise ValidationError(_('Passwords do not match'))


class SignInForm(FlaskForm):
    email = EmailField(_('E-mail adress'), validators=[InputRequired()])
    password = PasswordField(_('Password'), validators=[InputRequired()])


class RequestPassword(FlaskForm):
    email = EmailField(_('E-mail adress'), validators=[InputRequired()])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message='Check Recaptcha')])


class ResetPassword(FlaskForm):
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(),
            Length(message=(_('Minimal password length: %(length)d',
                              length=_min_password_length)),
                   min=_min_password_length)]
    )
    password_repeat = PasswordField(
        _('Repeat password'), validators=[
            InputRequired(),
            EqualTo('password', message=_('Passwords do not match'))]
    )
