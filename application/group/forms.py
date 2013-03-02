from flask.ext.wtf import Form, BooleanField, FormField, FieldList, SubmitField

class GroupEditEntry(Form):
	view = BooleanField('View')
	create = BooleanField('Create')
	edit = BooleanField('Edit')
	delete = BooleanField('Delete')

class GroupEditForm(Form):
	permissions = FieldList(FormField(GroupEditEntry))
	edit_group = SubmitField('Edit group')

