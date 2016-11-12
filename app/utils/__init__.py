from app import app

from .resource import Resource  # noqa

from .module import import_module  # noqa
from .serialize_sqla import serialize_sqla  # noqa

# OLD APIS
from .navigation import NavigationAPI
from .category import CategoryAPI
from .pimpy import PimpyAPI
from .page import PageAPI
from .seo import SeoAPI

from .user import UserAPI
from .module import ModuleAPI

app.jinja_env.globals.update(NavigationAPI=NavigationAPI)
app.jinja_env.globals.update(PimpyAPI=PimpyAPI)
app.jinja_env.globals.update(UserAPI=UserAPI)
app.jinja_env.globals.update(ModuleAPI=ModuleAPI)
app.jinja_env.globals.update(PageAPI=PageAPI)
app.jinja_env.globals.update(CategoryAPI=CategoryAPI)
app.jinja_env.globals.update(SeoAPI=SeoAPI)
