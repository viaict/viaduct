from viaduct import application

from course import CourseAPI
from degree import DegreeAPI
from education import EducationAPI
from navigation import NavigationAPI
from category import CategoryAPI
from pimpy import PimpyAPI
from file import FileAPI
from booksales import BookSalesAPI

from user import UserAPI
from group import GroupPermissionAPI
#from search import SearchAPI

CourseAPI.register()
DegreeAPI.register()
EducationAPI.register()

application.jinja_env.globals.update(NavigationAPI=NavigationAPI)
application.jinja_env.globals.update(PimpyAPI=PimpyAPI)
application.jinja_env.globals.update(UserAPI=UserAPI)
application.jinja_env.globals.update(GroupPermissionAPI=GroupPermissionAPI)
application.jinja_env.globals.update(BookSalesAPI=BookSalesAPI)
#application.jinja_env.globals(update(SearchAPI=SearchAPI)
application.jinja_env.globals.update(CategoryAPI=CategoryAPI)
