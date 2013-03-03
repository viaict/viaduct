from flask import flash, request

def flash_form_errors(form):
	for field, errors in form.errors.items():
		for error in errors:
			flash(error, 'error')

def find_subpages(pages, parent):
	subpages = []

	for page in pages:
		prefix = '/'.join(page.path.split('/')[:-1])
		if prefix == parent.path:
			subpages.append(page)

	return subpages

def get_current_page():
	if request.path.startswith('/page/'):
		return request.path[6:]
	return 'via'
