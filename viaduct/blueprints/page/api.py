import validictory

from viaduct import application

from flask import Markup
from flask import json, render_template, request
from flask.ext.login import current_user
from flask.ext.restful import Resource

from models import Page, PagePermission, PageRevision

class PageAPI2(Resource):
	@staticmethod
	def get(page_id=None):
		results = []

		query = Page.query

		if page_id:
			query = query.filter(Page.id==page_id)

		for page in query.all():
			results.append(page.to_dict())

		return results

	@staticmethod
	def post():
		return '', 201

	@staticmethod
	def put(page_id):
		data = request.json
		#page_schema = {'type': 'object', 'properties':
		#	{'path': {'type': 'string'}}
		#}
		page_schema = {'type': 'string'}

		try:
			validictory.validate(data, page_schema)
		except Exception:
			return '', '400 PLS STAHP'

		return {'content': data['content']}

class PageRevisionAPI(Resource):
	@staticmethod
	def get(page_id, revision_id=None):
		results = []

		page = Page.query.get(page_id)
		query = page.revisions

		if revision_id:
			query = query.filter(PageRevision.id==revision_id)

		for revision in query.all():
			results.append(revision.to_dict())

		return results

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
		print(path)

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
			title=revision.title, content_type=revision.content_type,
			content=revision.content))

	@staticmethod
	def get_page_history(path):
		return Markup(render_template('page/api/get_page_history'))

@application.route('/cry/me/a/river')
def lolwat():
	return PageAPI2.get()[0]['path']

