from flask.ext.wtf import Form, BooleanField, FormField, FieldList, SubmitField, \
		SelectField

class ViewGroupEntry(Form):
	select = BooleanField(None)

class ViewGroupForm(Form):
	entries = FieldList(FormField(ViewGroupEntry))
	delete_group = SubmitField('Delete group')


class EditGroupPermissionEntry(Form):
<<<<<<< HEAD
	select = SelectField(None, coerce=int, choices=[(0, "Geen"), (1, "Lees"), (2, "Lees/Schrijf")])

class EditGroupPermissionForm(Form):
	permissions = FieldList(FormField(EditGroupPermissionEntry))
	save_changes = SubmitField('Sla veranderingen op')

