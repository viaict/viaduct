from viaduct import application

from course import CourseAPI
from degree import DegreeAPI
from education import EducationAPI
from file import FileAPI
from navigation import NavigationAPI
from pimpy import PimpyAPI

CourseAPI.register()
DegreeAPI.register()
EducationAPI.register()
FileAPI.register()

application.jinja_env.globals.update(NavigationAPI=NavigationAPI)
application.jinja_env.globals.update(PimpyAPI=PimpyAPI)
