from viaduct import application

from views import module
from api import PimpyAPI

application.register_blueprint(module)
application.jinja_env.globals.update(PimpyAPI=PimpyAPI)


