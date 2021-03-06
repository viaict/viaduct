import datetime
import json

from flask import Markup, render_template
from flask_login import current_user
from markdown import markdown

from app import app, static_url, get_locale, constants, version
from app.forms.util import FormWrapper  # noqa
from app.utils import template_filters  # noqa
from app.utils.category import CategoryAPI  # noqa
from app.utils.company import CompanyAPI  # noqa
from app.utils.guide import GuideAPI  # noqa
from app.utils.navigation import NavigationAPI  # noqa
from app.utils.seo import get_seo_fields  # noqa
from app.utils.serialize_sqla import serialize_sqla  # noqa
from app.utils.user import UserAPI  # noqa

template_filters.register_filters(app)

# Set jinja global variables
app.jinja_env.globals.update(enumerate=enumerate)
app.jinja_env.globals.update(render_template=render_template)
app.jinja_env.globals.update(markdown=markdown)
app.jinja_env.globals.update(Markup=Markup)
app.jinja_env.globals.update(UserAPI=UserAPI)
app.jinja_env.globals.update(CompanyAPI=CompanyAPI)
app.jinja_env.globals.update(GuideAPI=GuideAPI)
app.jinja_env.globals.update(datetime=datetime)
app.jinja_env.globals.update(json=json)
app.jinja_env.globals.update(serialize_sqla=serialize_sqla)
app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(isinstance=isinstance)
app.jinja_env.globals.update(list=list)
app.jinja_env.globals.update(static_url=static_url)
app.jinja_env.globals.update(get_locale=get_locale)
app.jinja_env.globals.update(app_config=app.config)
app.jinja_env.globals.update(app_version=version)
app.jinja_env.globals.update(constants=constants)
app.jinja_env.globals.update(FormWrapper=FormWrapper)
app.jinja_env.globals.update(NavigationAPI=NavigationAPI)
app.jinja_env.globals.update(current_user=current_user)
app.jinja_env.globals.update(CategoryAPI=CategoryAPI)
app.jinja_env.globals.update(get_seo_fields=get_seo_fields)
