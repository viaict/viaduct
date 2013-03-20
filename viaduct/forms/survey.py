from flask.ext.wtf import Form, FieldList, FormField, SubmitField, BooleanField, HiddenField, SelectField

class SurveyFieldForm(Form):
	keep_alive = HiddenField('KeepAlive', default='keep-alive')
	field_type = SelectField('Field Type', choices=[('text', 'Text field'),
		('select', 'Select field'),
		('boolean', 'Boolean field')
	])
	view = BooleanField('View')

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(SurveyFieldForm, self).__init__(*args, **kwargs)

class CreateSurveyForm(Form):
	fields = FieldList(FormField(SurveyFieldForm))
	add_field = SubmitField('Add Field')
	create_survey = SubmitField('Create Survey')

