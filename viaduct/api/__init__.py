from viaduct import application

from course import CourseAPI
from degree import DegreeAPI
from education import EducationAPI
from navigation import NavigationAPI
from pimpy import PimpyAPI

CourseAPI.register()
DegreeAPI.register()
EducationAPI.register()

application.jinja_env.globals.update(NavigationAPI=NavigationAPI)
application.jinja_env.globals.update(PimpyAPI=PimpyAPI)
