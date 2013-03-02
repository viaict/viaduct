from flask.ext.wtf import Form, TextField, PasswordField, BooleanField, \
	RecaptchaField
from flask.ext.wtf import Required, Email, EqualTo

class SignUpForm(Form):
	email = TextField('E-mail address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])
	repeat_password = PasswordField('Repeat password', validators=[Required(),
		Equalto('password', message='The passwords do not match.')])
	first_name = TextField('First name', validators=[Required()])
	last_name = TextField('Last name', validators=[Required()])
	recaptcha = RecaptchaField()

class SignInForm(Form):
	email = TextField('E-mail address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Remember me', default = False)

