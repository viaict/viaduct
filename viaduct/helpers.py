from imp import find_module, load_module
from flask import flash, request, Markup
from viaduct import application
from markdown import markdown

markdown_extensions = [
	'toc'
]

def registers_blueprints(application, path):
	subpaths = os.listdir(path)

	for subpath in subpaths:
		name = name or os.path.split(subpath)[-1].replace('.', '_')
		fp, path, description = find_module(subpath)
		module = load_module(name, fp, path, description)
		application.register(getattr(module, 'blueprint'))

def flash_form_errors(form):
	for field, errors in form.errors.items():
		for error in errors:
			flash(error, 'error')

@application.template_filter('markdown')
def markdown_filter(data):
	return Markup(markdown(data, safe_mode='escape', enable_attributes=False,
		extensions=markdown_extensions))

@application.template_filter('safe_markdown')
def safe_markdown_filter(data):
	return Markup(markdown(data, extensions=markdown_extensions))

