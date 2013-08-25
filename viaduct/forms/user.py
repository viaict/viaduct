from flask.ext.wtf import Form, TextField, PasswordField, BooleanField, \
		RecaptchaField, SelectField, FieldList, FormField, SubmitField
from flask.ext.wtf import Required, Email, EqualTo, IntegerField
from flask.ext.wtf import ValidationError

class SignUpForm(Form):
	email = TextField('E-mail adres', validators=[Required(), Email()])
	password = PasswordField('Wachtwoord', validators=[Required()])
	repeat_password = PasswordField('Herhaal wachtwoord', validators=[Required(),
	EqualTo('password', message='De wachtwoorden komen niet overeen.')])
	first_name = TextField('Voornaam', validators=[Required()])
	last_name = TextField('Achternaam', validators=[Required()])
	student_id = TextField('Studentnummer', validators=[Required()])
	education_id = SelectField('Opleiding', coerce=int)
	recaptcha = RecaptchaField()

class EditUserForm(Form):
	id = IntegerField('ID')
	email = TextField('E-mail adres', validators=[Required(), Email()])
	password = PasswordField('Wachtwoord')
	repeat_password = PasswordField('Herhaal wachtwoord')
	first_name = TextField('Voornaam', validators=[Required()])
	last_name = TextField('Achternaam', validators=[Required()])
	has_payed = BooleanField('Heeft lidmaatschap betaald')
	student_id = TextField('Studentnummer', validators=[Required()])
	education_id = SelectField('Opleiding', coerce=int)

	def validate_password(form, field):
		"""Providing a password is only required when creating a new user."""
		if form.id.data == 0 and len(field.data) == 0:
			raise ValidationError('Geen wachtwoord opgegeven')

	def validate_repeat_password(form, field):
		"""Only validate the repeat password if a password is set."""
		if len(form.password.data) > 0 and field.data != form.password.data:
			raise ValidationError('Wachtwoorden komen niet overeen')


class SignInForm(Form):
	email = TextField('E-mail adres', validators=[Required(), Email()])
	password = PasswordField('Wachtwoord', validators=[Required()])
	remember_me = BooleanField('Onthouden', default = False)

#class EditUserPermissionEntry(Form):
#	select = SelectField(None, coerce=int, choices=[(1, 'Allow'), (-1, 'Deny'), (0, 'Inherit')])
#
#class EditUserPermissionForm(Form):
#	permissions = FieldList(FormField(EditUserPermissionEntry))
#	save_changes = SubmitField('Save changes')
