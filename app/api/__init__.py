from app import app

from .course import CourseAPI
from .degree import DegreeAPI
from .education import EducationAPI
from .navigation import NavigationAPI
from .category import CategoryAPI
from .pimpy import PimpyAPI
from .file import FileAPI  # noqa
from .booksales import BookSalesAPI
from .page import PageAPI

from .user import UserAPI
from .module import ModuleAPI

CourseAPI.register()
DegreeAPI.register()
EducationAPI.register()

app.jinja_env.globals.update(NavigationAPI=NavigationAPI)
app.jinja_env.globals.update(PimpyAPI=PimpyAPI)
app.jinja_env.globals.update(UserAPI=UserAPI)
app.jinja_env.globals.update(ModuleAPI=ModuleAPI)
app.jinja_env.globals.update(BookSalesAPI=BookSalesAPI)
app.jinja_env.globals.update(PageAPI=PageAPI)
app.jinja_env.globals.update(CategoryAPI=CategoryAPI)
