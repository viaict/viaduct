from viaduct import application

from api import PageAPI

application.jinja_env.globals.update(PageAPI=PageAPI)

