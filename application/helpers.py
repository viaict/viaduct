from flask import flash, request, Markup
from application import application
from markdown import markdown

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

@application.template_filter('markdown')
def markdown_filter(data):
	return Markup(markdown(data, safe_mode='escape', enable_attributes=False))
