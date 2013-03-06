from flask.ext.wtf import Form, BooleanField, FormField, FieldList, SubmitField

class GroupEditEntry(Form):
	view = BooleanField('View')
	create = BooleanField('Create')
	edit = BooleanField('Edit')
	delete = BooleanField('Delete')

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(GroupEditEntry, self).__init__(*args, **kwargs)

class GroupEditForm(Form):
	permissions = FieldList(FormField(GroupEditEntry))
	edit_group = SubmitField('Edit group')

