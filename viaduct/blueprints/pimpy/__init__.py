from viaduct import application

from api import PimpyAPI

application.jinja_env.globals.update(PimpyAPI=PimpyAPI)

