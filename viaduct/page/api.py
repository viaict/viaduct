from flask import Markup
from flask import render_template
from flask.ext.login import current_user

from models import Page, PagePermission

class PageAPI:
	@staticmethod
	def get_index_page(path):
		blocks = [ PageAPI.get_page('index/' + str(i)) for i in range(1, 5) ]

		return Markup(render_template('page/api/get_index_page.htm',
			blocks=blocks, path='via'))

	@staticmethod
	def get_error_page():
		return Markup(render_template('page/api/get_page.htm'))

	@staticmethod
	def get_page(path):
		if path == '' or path =='index' or path == 'via':
			return PageAPI.get_index_page(path)

		rights = PagePermission.get_user_rights(current_user, path)

		if not rights['view']:
			return PageAPI.get_error_page()

		page = Page.query.filter(Page.path==path).first()

		if not page:
			return PageAPI.get_error_page()

		revision = page.get_newest_revision()

		if not revision:
			return PageAPI.get_error_page()

		return Markup(render_template('page/api/get_page.htm',
			title=revision.title, content=revision.content))

