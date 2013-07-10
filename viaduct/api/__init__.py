from viaduct import application

from course import CourseAPI
from degree import DegreeAPI
from education import EducationAPI
from navigation import NavigationAPI
from pimpy import PimpyAPI
from file import FileAPI

from user import UserAPI
from module_permission import ModulePermissionAPI


CourseAPI.register()
DegreeAPI.register()
EducationAPI.register()

application.jinja_env.globals.update(NavigationAPI=NavigationAPI)
application.jinja_env.globals.update(PimpyAPI=PimpyAPI)
application.jinja_env.globals.update(UserAPI=UserAPI)
application.jinja_env.globals.update(ModulePermissionAPI=ModulePermissionAPI)
