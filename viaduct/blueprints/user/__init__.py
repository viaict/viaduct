from viaduct import application, login_manager

from views import module

application.register_blueprint(module)

