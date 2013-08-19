from flask import flash

def validate_form(form, fields):
	'''
	Validate that a form contains the in the fields list given information.
	Fields should be given as a list of field names.
	'''
	valid = True
	for field in fields:
		form_field = getattr(form, field)
		if not form_field.data:
			flash('Geen %s opgegeven' % (form_field.label.text.lower()),
					'error')
			valid = False

	return valid
