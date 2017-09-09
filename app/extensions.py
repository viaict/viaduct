from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from flask_debugtoolbar import DebugToolbarExtension
from raven.contrib.flask import Sentry
from flask_jsglue import JSGlue

from sqlalchemy import MetaData

cache = Cache()
toolbar = DebugToolbarExtension()
jsglue = JSGlue()
sentry = Sentry()


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
db = SQLAlchemy(metadata=MetaData(
    naming_convention=constraint_naming_convention,
    schema='viaduct'))

login_manager = LoginManager()
