from flask.ext.wtf import Form, BooleanField, FormField, FieldList, SubmitField, \
		SelectField

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

class EditGroupPermissionEntry(Form):
	select = SelectField(None, coerce=int, choices=[(1, 'Allow'), (-1, 'Deny')])

class EditGroupPermissionForm(Form):
	permissions = FieldList(FormField(EditGroupPermissionEntry))
	save_changes = SubmitField('Save changes')

