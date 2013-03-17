from viaduct import application

from api import NavigationAPI

application.jinja_env.globals.update(NavigationAPI=NavigationAPI)

