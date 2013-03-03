from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

# Set up the application and load the configuration file.
application = Flask(__name__)
application.config.from_object('config')

# Set up the login manager, which is used to store details related to the
# authentication system.
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'signin'

# Set up the database.
db = SQLAlchemy(application)

# Import the routing table for the application.
from application import views

# Import the routing tables for the modules.
from application.user.views import user
from application.group.views import group
from application.page.views import page_module
from application.navigation.views import view_bar, view_side_bar

application.register_blueprint(user)
application.register_blueprint(group)
application.register_blueprint(page_module)

# Register global views to be used within the template engine.
application.jinja_env.globals.update(test=views.test)
application.jinja_env.globals.update(render_navigation_bar=view_bar)
application.jinja_env.globals.update(render_sidenav=view_side_bar)

# Register the loader for the anonymous user.
from application.user.views import load_anonymous_user

login_manager.anonymous_user = load_anonymous_user

