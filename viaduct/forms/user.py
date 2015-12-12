# coding=utf-8

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, \
    SelectField, IntegerField, FileField
from wtforms.widgets import TextInput
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError,\
    Length, Optional
from config import LANGUAGES, MIN_PASSWORD_LENGTH

from flask.ext.babel import lazy_gettext as _  # noqa

import dateutil


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
    first_name = StringField(
        _('First name'), validators=[
            InputRequired(message=_('No first name sunmitted'))]
    )
    last_name = StringField(
        _('Last name'), validators=[
            InputRequired(message=_('No last name submitted'))]
    )
    student_id = StringField(
        _('Student number'), validators=[
            InputRequired(message=_('No studentnumber submitted'))]
    )
    education_id = SelectField('Opleiding', coerce=int)
    avatar = FileField('Avatar', validators=[Optional()])
    receive_information = BooleanField(_('Would you like to recieve information\
     from companies?'))

    phone_nr = StringField(_('Phone'))

    address = StringField(_('Address'))
    zip = StringField(_('Zipcode'))
    city = StringField(_('City'))
    country = StringField(_('Country'), default='Nederland')


class SignUpForm(BaseUserForm):
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(message=_('No password submitted')),
            Length(message=_('Minimal password length %d') %
                   MIN_PASSWORD_LENGTH, min=MIN_PASSWORD_LENGTH)]
    )
    repeat_password = PasswordField(
        _('Repeat password'), validators=[
            InputRequired(message=_('Passwords do not match')),
            EqualTo('password', message=_('Passwords do not match'))]
    )


class EditUserForm(BaseUserForm):
    """ Edit a user as administrator """
    id = IntegerField('ID')
    password = PasswordField(_('Password'))
    repeat_password = PasswordField(_('Repeat password'))
    has_payed = BooleanField(_('Has payed'))
    honorary_member = BooleanField(_('Honorary member'))
    locale = SelectField(_('Language'), choices=list(LANGUAGES.items()))
    favourer = BooleanField(_('Favourer'))

    birth_date = DateField(_('Birthdate'), validators=[
        InputRequired(message=_('No birthdate submitted'))])
    study_start = DateField(_('Start study'), validators=[
         InputRequired(message=_('No start study'))])

    def validate_password(form, field):
        """Providing a password is only required when creating a new user."""
        if form.id.data == 0 and len(field.data) == 0:
            raise ValidationError(_('No password submitted'))

    def validate_repeat_password(form, field):
        """Only validate the repeat password if a password is set."""
        if len(form.password.data) > 0 and field.data != form.password.data:
            raise ValidationError(_('Passwords do not match'))


class EditUserInfoForm(BaseUserForm):
    """ Edit your own user information """
    id = IntegerField('ID')
    password = PasswordField(
        _('Password'), validators=[
            Length(message=_('Minimal password length %d') %
                   MIN_PASSWORD_LENGTH, min=MIN_PASSWORD_LENGTH)]
        )
    repeat_password = PasswordField(
        _('Repeat password'), validators=[
            EqualTo('password', message=_('Passwords do not match'))]
    )

    def validate_password(form, field):
        """Providing a password is only required when creating a new user."""
        if form.id.data == 0 and len(field.data) == 0:
            raise ValidationError(_('No password submitted'))

    def validate_repeat_password(form, field):
        """Only validate the repeat password if a password is set."""
        if len(form.password.data) > 0 and field.data != form.password.data:
            raise ValidationError(_('Passwords do not match'))


class SignInForm(Form):
    email = StringField(_('E-mail adress'), validators=[
        InputRequired(message=_('No e-mail adress submitted')),
        Email(message=_('Invalid e-mail adress submitted'))])
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(message=_('No password submitted'))])


class RequestPassword(Form):
    email = StringField(_('E-mail adress'), validators=[
        InputRequired(message=_('No e-mail adress submitted')),
        Email(message=_('Invalid e-mail adress submitted'))])
    student_id = StringField(
        _('Studentnumber'), validators=[
            InputRequired(message=_('No studentnumber submitted'))]
    )


class ResetPassword(Form):
    password = PasswordField(
        _('Password'), validators=[
            InputRequired(message=_('No password submitted')),
            Length(message=_('Minimal password length %d') %
                   MIN_PASSWORD_LENGTH, min=MIN_PASSWORD_LENGTH)]
    )
    password_repeat = PasswordField(
        _('Repeat password'), validators=[
            InputRequired(message=_('Passwords do not match')),
            EqualTo('password', message=_('Passwords do not match'))]
    )
