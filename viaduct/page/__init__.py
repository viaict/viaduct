from viaduct import application

from views import module
from api import PageAPI

application.register_blueprint(module)

application.jinja_env.globals.update(PageAPI=PageAPI)

