from flask.ext.wtf import Form, TextField, TextAreaField, Required

# Who let the dogs out... otherwise form parser gives an error
class CreateForm(Form):
	name	= TextField(u'Name', validators=[Required()])
	origin	= TextField(u'Who')
	html	= TextField(u'Let the dogs out')
