# coding=utf-8
from flask_babel import lazy_gettext as _  # noqa
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField, Recaptcha
from wtforms import StringField, PasswordField, BooleanField, \
    SelectField, FileField, DateField
from wtforms.validators import (InputRequired, EqualTo, Length,
                                Optional, ValidationError)

from app import app
from app.forms.fields import EmailField
from app.forms.util import FieldVerticalSplit

from datetime import datetime
from dateutil.relativedelta import relativedelta

_min_password_length = app.config['MIN_PASSWORD_LENGTH']


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        _('New password'), validators=[
            InputRequired(),
            Length(message=(_('Minimal password length: %(length)d',
                              length=_min_password_length)),
                   min=_min_password_length)]
    )
    password_repeat = PasswordField(
        _('Repeat new password'), validators=[
            InputRequired(),
            EqualTo('password', message=_('Passwords do not match'))]
    )


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


class SignUpForm(BaseUserForm, ResetPasswordForm):
    birth_date = DateField(_('Birthdate'), validators=[
        InputRequired()])
    study_start = DateField(_('Starting year study'), validators=[
        InputRequired()])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message='Check Recaptcha')])

    register_split = FieldVerticalSplit([
        ['first_name', 'last_name', 'birth_date', 'address', 'zip', 'city',
         'country', 'recaptcha'],
        ['email', 'password', 'password_repeat', 'student_id', 'education_id',
         'study_start', 'receive_information']
    ], large_spacing=True)

    _RenderIgnoreFields = ['locale', 'phone_nr', 'avatar']

    def validate_birth_date(self, field):
        sixteen_years_ago = datetime.now().date() - relativedelta(years=16)

        if field.data > sixteen_years_ago:
            raise ValidationError(_('You need to be at least 16 years old.'))


class EditUserForm(BaseUserForm):
    """Edit a user as administrator."""

    has_paid = BooleanField(_('Has paid'))
    honorary_member = BooleanField(_('Honorary member'))
    favourer = BooleanField(_('Favourer'))
    disabled = BooleanField(_('Disabled'))

    register_split = FieldVerticalSplit([
        ['first_name', 'last_name', 'address', 'zip', 'city', 'country'],
        ['email', 'student_id', 'education_id', 'birth_date',
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


class EditUserInfoForm(BaseUserForm):
    """Edit your own user information."""

    alumnus = BooleanField(_('Yes, I have finished studying'))

    register_split = FieldVerticalSplit([
        ['first_name', 'last_name', 'address', 'zip', 'city', 'country'],
        ['email', 'student_id', 'education_id', 'birth_date', 'study_start']
    ], large_spacing=True)

    optional_split = FieldVerticalSplit([
        ['phone_nr', 'locale'],
        ['avatar']
    ], large_spacing=True)

    new_user = False


class SignInForm(FlaskForm):
    email = EmailField(_('E-mail adress'), validators=[InputRequired()])
    password = PasswordField(_('Password'), validators=[InputRequired()])


class RequestPassword(FlaskForm):
    email = EmailField(_('E-mail adress'), validators=[InputRequired()])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message='Check Recaptcha')])


class ChangePasswordForm(ResetPasswordForm):
    current_password = PasswordField(
        _('Current Password'), validators=[
            InputRequired(),
            Length(
                message=(_('Minimal password length: %(length)d',
                           length=_min_password_length)),
                min=_min_password_length)]
    )
