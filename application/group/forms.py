from flask.ext.wtf import Form, BooleanField, FormField, FieldList

class GroupEditEntry(Form):
	view = BooleanField('View')
	create = BooleanField('Create')
	edit = BooleanField('Edit')
	delete = BooleanField('Delete')

class GroupEditForm(Form):
	permissions = FieldList(FormField(GroupEditEntry))

