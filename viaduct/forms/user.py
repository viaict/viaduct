from flask.ext.wtf import Form, TextField, PasswordField, BooleanField, \
		RecaptchaField, SelectField, FieldList, FormField, SubmitField
from flask.ext.wtf import Required, Email, EqualTo

class SignUpForm(Form):
	email = TextField('E-mail address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])
	repeat_password = PasswordField('Repeat password', validators=[Required(),
		EqualTo('password', message='The passwords do not match.')])
	first_name = TextField('First name', validators=[Required()])
	last_name = TextField('Last name', validators=[Required()])
	student_id = TextField('Student ID', validators=[Required()])
	recaptcha = RecaptchaField()

class SignUpFormNoCaptcha(Form):
	email = TextField('E-mail address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])
	repeat_password = PasswordField('Repeat password', validators=[Required(),
		EqualTo('password', message='The passwords do not match.')])
	first_name = TextField('First name', validators=[Required()])
	last_name = TextField('Last name', validators=[Required()])
	student_id = TextField('Student ID', validators=[Required()])

class SignInForm(Form):
	email = TextField('E-mail address', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Remember me', default = False)

class EditUserPermissionEntry(Form):
	select = SelectField(None, coerce=int, choices=[(1, 'Allow'), (-1, 'Deny'), (0, 'Inherit')])

class EditUserPermissionForm(Form):
	permissions = FieldList(FormField(EditUserPermissionEntry))
	save_changes = SubmitField('Save changes')

