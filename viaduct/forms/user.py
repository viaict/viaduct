# coding=utf-8

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, \
    SelectField, IntegerField, FileField
from wtforms.widgets import TextInput
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError,\
    Length, Optional
from config import LANGUAGES, MIN_PASSWORD_LENGTH

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


class SignUpForm(Form):
    email = StringField('E-mailadres', validators=[
        InputRequired(message='Geen e-mailadres opgegeven'),
        Email(message='Ongelding e-mailadres opgegeven')])
    password = PasswordField(
        'Wachtwoord', validators=[
            InputRequired(message='Geen wachtwoord opgegeven'),
            Length(message='Minumum wachtwoord length: %d' %
                   MIN_PASSWORD_LENGTH, min=MIN_PASSWORD_LENGTH)]
    )
    repeat_password = PasswordField(
        'Herhaal wachtwoord', validators=[
            InputRequired(message='Wacht woorden komen niet overeen'),
            EqualTo('password', message='Wachtwoorden komen niet overeen')]
    )
    first_name = StringField(
        'Voornaam', validators=[
            InputRequired(message='Geen voornaam opgegeven')]
    )
    last_name = StringField(
        'Achternaam', validators=[
            InputRequired(message='Geen achternaam opgegeven')]
    )
    student_id = StringField(
        'Studentnummer', validators=[
            InputRequired(message='Geen studentnummer opgegeven')]
    )
    education_id = SelectField('Opleiding', coerce=int)
    avatar = FileField('Avatar', validators=[Optional()])
    receive_information = BooleanField('Wil je informatie van bedrijven\
        ontvangen?')

    birth_date = DateField('Geboortedatum', validators=[
        InputRequired(message='Geen geboortedatum opgegeven')])
    study_start = DateField('Begin studie', validators=[
        InputRequired(message='Geen begin studie opgegeven')])


class EditUserForm(Form):
    """ Edit a user as administrator """
    id = IntegerField('ID')
    email = StringField(
        'E-mailadres', validators=[
            InputRequired(message='Geen e-mailadres opgegeven'),
            Email(message='Ongeldig e-mailadres opgegeven')]
    )
    password = PasswordField('Wachtwoord')
    repeat_password = PasswordField('Herhaal wachtwoord')
    first_name = StringField(
        'Voornaam', validators=[
            InputRequired(message='Geen voornaam opgegeven')]
    )
    last_name = StringField(
        'Achternaam', validators=[
            InputRequired(message='Geen achternaam opgegeven')]
    )
    has_payed = BooleanField('Heeft betaald')
    honorary_member = BooleanField('Erelid')
    locale = SelectField('Taal', choices=list(LANGUAGES.items()))
    favourer = BooleanField('Begunstiger')
    student_id = StringField(
        'Studentnummer', validators=[
            InputRequired(message='Geen studentnummer opgegeven')]
    )
    education_id = SelectField('Opleiding', coerce=int)
    avatar = FileField('Avatar', validators=[Optional()])
    birth_date = DateField('Geboortedatum')
    study_start = DateField('Begin studie')

    def validate_password(form, field):
        """Providing a password is only required when creating a new user."""
        if form.id.data == 0 and len(field.data) == 0:
            raise ValidationError('Geen wachtwoord opgegeven')

    def validate_repeat_password(form, field):
        """Only validate the repeat password if a password is set."""
        if len(form.password.data) > 0 and field.data != form.password.data:
            raise ValidationError('Wachtwoorden komen niet overeen')


class EditUserInfoForm(Form):
    """ Edit your own user information """
    id = IntegerField('ID')
    email = StringField(
        'E-mailadres', validators=[
            InputRequired(message='Geen e-mailadres opgegeven'),
            Email(message='Ongeldig e-mailadres opgegeven')])
    password = PasswordField(
        'Wachtwoord', validators=[
            Length(message='Minumum wachtwoord length: %d' %
                   MIN_PASSWORD_LENGTH, min=MIN_PASSWORD_LENGTH)]
        )
    repeat_password = PasswordField(
        'Herhaal wachtwoord', validators=[
            EqualTo('password', message='Wachtwoorden komen niet overeen')]
    )
    first_name = StringField(
        'Voornaam', validators=[
            InputRequired(message='Geen voornaam opgegeven')])
    last_name = StringField(
        'Achternaam', validators=[
            InputRequired(message='Geen achternaam opgegeven')])
    student_id = StringField(
        'Studentnummer', validators=[
            InputRequired(message='Geen studentnummer opgegeven')])

    locale = SelectField('Taal', choices=list(LANGUAGES.items()))
    education_id = SelectField('Opleiding', coerce=int)
    avatar = FileField('Avatar', validators=[Optional()])
    birth_date = DateField('Geboortedatum')
    study_start = DateField('Begin studie')
    receive_information = BooleanField('Wil je informatie van bedrijven\
        ontvangen?')

    def validate_password(form, field):
        """Providing a password is only required when creating a new user."""
        if form.id.data == 0 and len(field.data) == 0:
            raise ValidationError('Geen wachtwoord opgegeven')

    def validate_repeat_password(form, field):
        """Only validate the repeat password if a password is set."""
        if len(form.password.data) > 0 and field.data != form.password.data:
            raise ValidationError('Wachtwoorden komen niet overeen')


class SignInForm(Form):
    email = StringField(
        'E-mailadres', validators=[
            InputRequired(message='Geen e-mailadres opgegeven'),
            Email(message='Ongeldig e-mailadres opgegeven')])
    password = PasswordField(
        'Wachtwoord', validators=[
            InputRequired(message='Geen wachtwoord opgegeven')])


class RequestPassword(Form):
    email = StringField(
        'E-mailadres', validators=[
            InputRequired(message='Geen e-mailadres opgegeven'),
            Email(message='Ongeldig e-mailadres opgegeven')])
    student_id = StringField(
        'Studentnummer', validators=[
            InputRequired(message='Geen studentnummer opgegeven')])


class ResetPassword(Form):
    password = PasswordField(
        'Wachtwoord', validators=[
            InputRequired(message='Geen wachtwoord opgegeven'),
            Length(message='Minumum wachtwoord length: %d' %
                   MIN_PASSWORD_LENGTH, min=MIN_PASSWORD_LENGTH)]
    )
    password_repeat = PasswordField(
        'Herhaal wachtwoord', validators=[
            InputRequired(message='Wachtwoorden komen niet overeen'),
            EqualTo('password', message='Wachtwoorden komen niet overeen')]
    )
