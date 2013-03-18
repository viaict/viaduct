from viaduct import application

from api import PageAPI, PageAPI2, PageRevisionAPI

application.jinja_env.globals.update(PageAPI=PageAPI)

