from flask import flash, request, Markup, url_for, render_template
from flask.ext.login import current_user

from viaduct import application
from markdown import markdown
from resource import Resource

from viaduct.models.activity import Activity

import datetime

markdown_extensions = [
	'toc'
]

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

@application.template_filter('pages')
def pages_filter(data):
	print "DAAAAAAAATA"
	for i in range(len(data)):
		print i, data[i].title

	content = '<div class="container">'

	for i in range(len(data)):
		if i % 2 == 0:
			content += '<div class="row">'

		if i == len(data) - 1 and i % 2 == 0:
			content += '<div class="span10">'
		else:
			content += '<div class="span6">'

		content += '<div class="mainblock'
		# expander toevoegen als het over de mainpage gaat
		content += ' expander">' if data[i].is_main_page else '">'
	
		if current_user.is_authenticated():
			content += '<div class="btn-group">'
			content += '<a class="btn" href="' + url_for(
				'page2.get_page_history', path=data[i].path) + '"><i class="icon-time"></i> View History</a>'
			content += '<a class="btn" href="' + url_for('page2.edit_page',
				path=data[i].path) + '"><i class="icon-pencil"></i> Edit Page</a>'
			content += '</div>'


		if data[i].is_main_page:
			if data[i].path == 'twitter':
				content += '<h1>{0}</h1>'.format(data[i].title)
				content += markdown(data[i].content,
					enable_attributes=False, extensions=markdown_extensions)
			elif data[i].path == 'activities':
				activities = Activity.query \
					.filter(Activity.end_time > datetime.datetime.now()) \
					.order_by(Activity.start_time.asc())
				content += render_template('activity/view_simple.htm',
					activities=activities.paginate(1, 12, False))
			elif data[i].path == 'contact' or data[i].path == 'laatste_bestuursblog':
				content += '<h1>{0}</h1>'.format(data[i].title)
				content += markdown(data[i].content, extensions=markdown_extensions)
		else:
			print data[i].path
			content += '<h1>{0}</h1>'.format(data[i].title)
			content += markdown(data[i].content, extensions=markdown_extensions)

		## we fix index/homepage here
		#if i == 1 and data[i].filter_html:
		#	content += '<h1>{0}</h1>'.format(data[i].title)
		#	content += markdown(data[i].content,
		#		enable_attributes=False, extensions=markdown_extensions)
		#elif i == 2:
		#	activities = Activity.query \
		#		.filter(Activity.end_time > datetime.datetime.now()) \
		#		.order_by(Activity.start_time.asc())
		#	content += markdown(render_template('activity/view_simple.htm',
		#		activities=activities.paginate(1, 12, False)))
		#else:
		#content += '<h1>{0}</h1>'.format(data[i].title)
		#content += markdown(data[i].content, extensions=markdown_extensions)

		content += '</div></div>'

		if i == len(data) - 1 or i % 2 != 0:
			content += '</div>'

	content += '</div>'

	return Markup(content)

