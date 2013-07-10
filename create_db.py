import os, bcrypt, datetime
from viaduct import db, application

from viaduct.models.page import Page, PagePermission, PageRevision

from viaduct.models import User, UserPermission, Group, GroupPermission
from viaduct.models import Activity
from viaduct.models import Minute, Task
from viaduct.models import NavigationEntry

from viaduct.models.permission import Permission
from viaduct.models.vacancy import Vacancy
from viaduct.models.requirement import Requirement
from viaduct.models.education import Education
from viaduct.models.programming_language import ProgrammingLanguage
from viaduct.models.company import Company
from viaduct.models.location import Location
from viaduct.models.contact import Contact
from viaduct.models.custom_form import CustomForm, CustomFormResult

# Remove the old db.
if os.path.exists('application.db'):
	os.remove('application.db')

# Create the database.
db.create_all()

page = Page('')

db.session.add(page)
db.session.commit()

# Add the anonymous user.
user = User()

db.session.add(user)
db.session.commit()

# Add the administrator.
user = User('administrator@svia.nl', bcrypt.hashpw('ictIsAwesome',
		bcrypt.gensalt()), 'Administrator', '', '0')

db.session.add(user)
db.session.commit()

# Add the administrators group.
group = Group('administrators')

db.session.add(group)
db.session.commit()

permissions = {
	'user.view': 'View Users',
	'user.create': 'Create Users',
	'user.edit': 'Edit Users',
	'user.delete': 'Delete Users',
	'group.view': 'View Groups',
	'group.create': 'Create Groups',
	'group.edit': 'Edit Groups',
	'group.delete': 'Delete Groups',
}

for key, value in permissions.items():
	permission = Permission(key, value)
	db.session.add(permission)
	db.session.commit()
	db.session.add(GroupPermission(group, permission))
	db.session.commit()

# Add the administrator to the administrators group.
group.add_user(user)

db.session.add(group)
db.session.commit()

# Grant the permissions.
permissions = PagePermission(group, page, view=True, create=True, edit=True,
	delete=True)

db.session.add(permissions)
db.session.commit()


# Add stuff for pimpystuff for pimpy

#user_maarten = User('maarten@maarten.mrt', bcrypt.hashpw('administrator', bcrypt.gensalt()), 'Maarten', 'Inja')
#user_ed = User('ed@ed.eds', bcrypt.hashpw('administrator', bcrypt.gensalt()), 'Handsome', 'Ed')
#group_first = Group('first')
#group_second = Group('second')
#
#
## Add the anonymous user.
#user = User('-0', '-0', 'Klaas', 'Vaak')
#db.session.add(user)
#db.session.commit()
#
#user = User('-1', '-1', 'Computer', 'Rekenmachine')
#db.session.add(user)
#db.session.commit()
#
#
## could I add more stuff at once?
#db.session.add(user_maarten)
#db.session.commit()
#db.session.add(user_ed)
#db.session.commit()
#db.session.add(group_first)
#db.session.commit()
#db.session.add(group_second)
#db.session.commit()
#
#group_first.add_user(user_maarten)
#group_first.add_user(user_ed)
#group_first.add_user(user)
#group_second.add_user(user_maarten)
#group_second.add_user(user_ed)
#group_second.add_user(user)
#
#db.session.add(group_first)
#db.session.commit()
#db.session.add(group_second)
#db.session.commit()
#
#
#'''
#self.name = name
#self.description = description
#self.start_time = start_time
#self.end_time = end_time
#self.location = location
#self.price = price
#self.picture = picture
#'''

activity1 = Activity()
activity1.start_time = datetime.datetime(2012, 10, 10, 17, 0)
activity1.end_time = datetime.datetime(2012, 10, 10, 22, 0)
activity1.name = "Een activiteit in het verleden"
activity1.description = """According to some, the system that is designed during the 19th century is on the verge of a revolution. A revolution that could radically change the way we educate ourselves and others, and even the way we look at education. But whether it is a revolution or just an evolution, technology is undoubtedly beginning to play a serious role in many forms of education. Over time, teaching transformed from one on one tutoring to mass education. And the emergence of the internet is now pushing education to the largest scale in history with the introduction of Massive Open Online Courses (early MOOCs had 100000 enrollments). At the same time, education (not unlike the rest of life) is increasingly leaving digital traces.

Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""

activity2 = Activity()
activity2.start_time = datetime.datetime(2013, 10, 10, 17, 0)
activity2.end_time = datetime.datetime(2013, 10, 10, 22, 0)
activity2.name = "Een activiteit in het heden"
activity2.description = """Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""

db.session.add(activity1)
db.session.add(activity2)
db.session.commit()

#minute = Minute("minute content, jaja", 2, datetime.date(2020, 10, 10))
#db.session.add(minute)
#db.session.commit()
#
## task
##	def __init__(self, title, content, deadline, group_id, users,
##				minute_id, line, status):
#
#task0 = Task('test task', 'test content', datetime.date(2020, 10, 10), group_first.id, [user, user_maarten], 1, minute.id, 0)
#db.session.add(task0)
#db.session.commit()
#
#task1 = Task('finish godamn pimpy', 'content', datetime.date(2015, 11, 9), group_second.id, [user, user_maarten, user_ed], 1, minute.id, 0)
#db.session.add(task1)
#db.session.commit()
#
#
#task2 = Task('I dont even', 'sja', datetime.date(2017, 12, 15), group_second.id, [user_maarten, user_ed], 1, minute.id, 0)
#db.session.add(task2)
#db.session.commit()
#
## Do some pages.
#page = Page('page1')
#db.session.add(page)
#db.session.commit()

permissions = PagePermission(group, page, view=True, create=True, edit=True,
		delete=True)
db.session.add(permissions)
db.session.commit()

revision = PageRevision(page, user, 'Page 1', 'herr derr 1', 0)
db.session.add(revision)
db.session.commit()

nav_home = NavigationEntry(None, 'Home', '/', False, False, 1)
db.session.add(nav_home)
db.session.commit()

nav_page1 = NavigationEntry(None, 'Pagina 1', '/page1', False, False, 2)
db.session.add(nav_page1)
db.session.commit()

nav_admin = NavigationEntry(None, 'Admin', '/admin', False, False, 3)
db.session.add(nav_admin)
db.session.commit()

nav_nav = NavigationEntry(nav_admin, 'Navigatie', '/navigation', False, False, 1)
db.session.add(nav_nav)
db.session.commit()

nav_activity = NavigationEntry(None, 'Activiteiten', '/activities', False, True, 4)
db.session.add(nav_activity)
db.session.commit()

nav_ext = NavigationEntry(nav_page1, 'Externaal', 'viaduct.svia.nl', True, False, 1)
db.session.add(nav_ext)
db.session.commit()

nav_vacancies = NavigationEntry(None, 'Vacaturebank', '/vacancies/', False, False, 5)
db.session.add(nav_vacancies)
db.session.commit()

nav_companies = NavigationEntry(None, 'Bedrijven', '/companies/', False, False, 6)
db.session.add(nav_companies)
db.session.commit()

# VACANCIES

location_1 = Location('Amsterdam', 'The Netherlands', 'Science Park 904',
		'1098 XH', 'nvt', 'email@sciencepark.nl', '2345613452')
db.session.add(location_1)
db.session.commit()

location_2 = Location('Utrecht', 'The Netherlands', 'Drol 2', '1333 DD',
		'2 uur', 'geen', 'geen')
db.session.add(location_2)
db.session.commit()

contact_1 = Contact('Bas de Boer', 'jemoeder@jemoder.nl', '12', location_1)
db.session.add(contact_1)
db.session.commit()

company_1 = Company('test', 'bladiebla', datetime.datetime.now(),
		datetime.datetime.now(), location_1, contact_1)
db.session.add(company_1)
db.session.commit()

vacancy_1 = Vacancy('test', 'bladiebla', datetime.datetime.now(),
		datetime.datetime.now(), 'deeltijd', 'nvt', company_1)
db.session.add(vacancy_1)
db.session.commit()
