from viaduct import api_manager, application

from api import PageAPI, PageAPI2, PageRevisionAPI

api_manager.add_resource(PageAPI2, '/api/pages', '/api/pages/<int:page_id>')
api_manager.add_resource(PageRevisionAPI, '/api/pages/<int:page_id>/revisions',
	'/api/pages/<int:page_id>/revisions/<int:revision_id>')

application.jinja_env.globals.update(PageAPI=PageAPI)

