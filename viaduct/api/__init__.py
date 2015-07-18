from viaduct import application

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

application.jinja_env.globals.update(NavigationAPI=NavigationAPI)
application.jinja_env.globals.update(PimpyAPI=PimpyAPI)
application.jinja_env.globals.update(UserAPI=UserAPI)
application.jinja_env.globals.update(ModuleAPI=ModuleAPI)
application.jinja_env.globals.update(BookSalesAPI=BookSalesAPI)
application.jinja_env.globals.update(PageAPI=PageAPI)
application.jinja_env.globals.update(CategoryAPI=CategoryAPI)
