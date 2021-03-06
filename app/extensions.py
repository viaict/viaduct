from authlib.flask.oauth2 import AuthorizationServer
from flask_babel import Babel
from flask_caching import Cache
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from sqlalchemy import MetaData

cache = Cache()
cors = CORS()
toolbar = DebugToolbarExtension()
jsglue = JSGlue()
sentry = Sentry()
oauth_server = AuthorizationServer()
babel = Babel()

# Set up the database.
constraint_naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Custom SQLAlchemy object that uses naming conventions.
# https://stackoverflow.com/questions/29153930/
metadata = MetaData(naming_convention=constraint_naming_convention)
db = SQLAlchemy(metadata=metadata)

login_manager = LoginManager()
