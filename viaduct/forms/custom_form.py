from flask.ext.wtf import Form, TextField, TextAreaField, Required, SubmitField

# Who let the dogs out... otherwise form parser gives an error
class CreateForm(Form):
	name	= TextField(u'Formulier naam', validators=[Required()])
	origin	= TextField(u'Who')
	html	= TextField(u'Let the dogs out')
	submit = SubmitField('Opslaan')
