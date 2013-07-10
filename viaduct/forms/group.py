from flask.ext.wtf import Form, BooleanField, FormField, FieldList, SubmitField, \
		SelectField

class ViewGroupEntry(Form):
	select = BooleanField(None)

class ViewGroupForm(Form):
	entries = FieldList(FormField(ViewGroupEntry))
	delete_group = SubmitField('Delete group')

class EditGroupPermissionEntry(Form):
	select = SelectField(None, coerce=int, choices=[(1, 'Allow'), (-1, 'Deny')])
	
class EditGroupPermissionForm(Form):
	permissions = FieldList(FormField(EditGroupPermissionEntry))
	save_changes = SubmitField('Save changes')

