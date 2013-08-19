import os, bcrypt, datetime
from viaduct import db, application

from viaduct.models.page import Page, PagePermission, PageRevision

from viaduct.models import User, Group, GroupPermission
from viaduct.models import Activity
from viaduct.models import Minute, Task
from viaduct.models import NavigationEntry
#from viaduct.models.module_permission import ModulePermission

#from viaduct.models.permission import Permission
from viaduct.models.vacancy import Vacancy
from viaduct.models.requirement import Requirement
from viaduct.models.education import Education
from viaduct.models.programming_language import ProgrammingLanguage
from viaduct.models.company import Company
from viaduct.models.location import Location
from viaduct.models.contact import Contact
from viaduct.models.custom_form import CustomForm, CustomFormResult
from viaduct.models.file import File

# Remove the old db.
if os.path.exists('application.db'):
	os.remove('application.db')

# Create the database.
db.create_all()

page = Page('')
db.session.add(page)
db.session.commit()

#Add the all group
group_all = Group('all')

db.session.add(group_all)
db.session.commit()

# Add the anonymous user.
user = User()
db.session.add(user)
db.session.commit()

# Add the administrator.
user = User('administrator@svia.nl', bcrypt.hashpw('ictIsAwesome',
		bcrypt.gensalt()), 'Administrator', 'de beste', '0')

db.session.add(user)
db.session.commit()

group_all.add_user(user)

db.session.add(group_all)
db.session.commit()

# Add the administrators group.
group = Group('administrators')

db.session.add(group)
db.session.commit()

# a group for not logged in users
group_guest = Group('guests')
db.session.add(group_guest)
db.session.commit()


# Add the administrator to the administrators group.
group.add_user(user)

db.session.add(group)
db.session.commit()

# Grant the permissions.
#permissions = PagePermission(group, page, permission=2)

#db.session.add(permissions)
#db.session.commit()


# Add stuff for pimpystuff for pimpy

user_tijmen = User('tijmen.zwaan@gmail.com', bcrypt.hashpw('memorystick', bcrypt.gensalt()), 'Tijmen', 'Zwaan')
group_ict = Group('ict')
group_bestuur = Group('bestuur')
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
db.session.add(user_tijmen)
db.session.add(group_ict)
db.session.add(group_bestuur)
db.session.commit()
#db.session.add(user_maarten)
#db.session.commit()
#db.session.add(user_ed)
#db.session.commit()
#db.session.add(group_first)
#db.session.commit()
#db.session.add(group_second)
#db.session.commit()

group_ict.add_user(user_tijmen)
group_bestuur.add_user(user_tijmen)
group.add_user(user_tijmen)
db.session.commit()
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

custom_form = CustomForm(user.id, "Test formulier", '''Dieet | checkbox
-Vegetarisch
-Veganistisch

Shirt maat | select
-Small
-Medium
-Large

Noodnummer
> Telefoon nummer in geval van nood
Allergie/medicatie | textarea

> Waar moeten we rekening mee houden''', '''<div id="custom_form_data"><div class="control-group"><label class="control-label">Dieet </label><div class="controls"><div name="dieet"><label class="checkbox"><input type="checkbox" name="dieet[]" value="Vegetarisch"> Vegetarisch</label><label class="checkbox"><input type="checkbox" name="dieet[]" value="Veganistisch"> Veganistisch</label></div></div></div><div class="control-group"><label class="control-label">Shirt maat </label><div class="controls"><select name="shirt maat"><option>Small</option><option>Medium</option><option>Large</option></select></div></div><div class="control-group"><label class="control-label">Noodnummer</label><small> Telefoon nummer in geval van nood</small><div class="controls"><input type="text" name="noodnummer"></div></div><div class="control-group"><label class="control-label">Allergie/medicatie </label><small> Waar moeten we rekening mee houden</small><div class="controls"><textarea name="allergie/medicatie"></textarea></div></div></div>''')

db.session.add(custom_form)
db.session.commit()

activity1 = Activity()
activity1.start_time = datetime.datetime(2012, 10, 10, 17, 0)
activity1.end_time = datetime.datetime(2012, 10, 10, 22, 0)
activity1.name = "Een activiteit in het verleden"
activity1.description = """According to some, the system that is designed during the 19th century is on the verge of a revolution. A revolution that could radically change the way we educate ourselves and others, and even the way we look at education. But whether it is a revolution or just an evolution, technology is undoubtedly beginning to play a serious role in many forms of education. Over time, teaching transformed from one on one tutoring to mass education. And the emergence of the internet is now pushing education to the largest scale in history with the introduction of Massive Open Online Courses (early MOOCs had 100000 enrollments). At the same time, education (not unlike the rest of life) is increasingly leaving digital traces.

Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""

activity2 = Activity()
activity2.form_id = custom_form.id
activity2.start_time = datetime.datetime(2013, 10, 10, 17, 0)
activity2.end_time = datetime.datetime(2013, 10, 10, 22, 0)
activity2.name = "Een activiteit die nog moet komen, met formulier"
activity2.description = """Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""

activity3 = Activity()
activity3.start_time = datetime.datetime(2013, 10, 10, 17, 0)
activity3.end_time = datetime.datetime(2013, 10, 10, 22, 0)
activity3.name = "Een activiteit in het heden"
activity3.description = """Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""

activity4 = Activity()
activity4.start_time = datetime.datetime(2013, 10, 10, 17, 0)
activity4.end_time = datetime.datetime(2013, 10, 10, 22, 0)
activity4.name = "Een activiteit in het heden"
activity4.description = """Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""


activity5 = Activity()
activity5.start_time = datetime.datetime(2013, 10, 10, 17, 0)
activity5.end_time = datetime.datetime(2013, 10, 10, 22, 0)
activity5.name = "Een activiteit in het heden"
activity5.description = """Learning analytics is a fairly recent technology that takes advantage of these traces. As most technologies it can be used for multiple purposes and can serve both the revolution and the evolution perspectives.

In this talk I want to elaborate a little bit on the traditional model of education and present the core of the revolution. We'll discuss the current influences that technology can have on education by examining some well known examples. I'll explain what we mean with Learning Analytics, how it might work (technically), what it's potential seems to be, and, of course, what the possible downsides are. We'll conclude with discussing various visions of the future of learning and their potential impact on society.

Although I will not apply the personalization to this talk, I'll attempt to put something in there for everybody. It is then up to you to interact with me and each other to bend it to the perfect talk."""


db.session.add(activity1)
db.session.add(activity2)
db.session.add(activity3)
db.session.add(activity4)
db.session.add(activity5)
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

nav_forms = NavigationEntry(nav_admin, 'Formulieren', '/forms/', False, False, 2)
db.session.add(nav_forms)
db.session.commit()

nav_activity = NavigationEntry(None, 'Activiteiten', '/activities', False, True, 4)
db.session.add(nav_activity)
db.session.commit()

nav_ext = NavigationEntry(nav_page1, 'Externaal', 'viaduct.svia.nl', True, False, 1)
db.session.add(nav_ext)
db.session.commit()

nav_pimpy = NavigationEntry(None, 'Pimpy', '/pimpy', False, False, 5)
db.session.add(nav_pimpy)

nav_vacancies = NavigationEntry(None, 'Vacaturebank', '/vacancies/', False, False, 5)
db.session.add(nav_vacancies)
db.session.commit()

nav_companies = NavigationEntry(None, 'Bedrijven', '/companies/', False, False, 6)
db.session.add(nav_companies)
db.session.commit()

nav_locations = NavigationEntry(None, 'Locaties', '/locations/', False, False, 7)
db.session.add(nav_locations)
db.session.commit()

nav_contacts = NavigationEntry(None, 'Contactpersonen', '/contacts/', False, False, 7)
db.session.add(nav_contacts)
db.session.commit()

nav_files = NavigationEntry(None, 'Bestanden', '/files/', False, False, 8)
db.session.add(nav_files)
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


# MODULE_PERMISSION
# group should still be administrators!!!

# in the future we want modules to automagically register themselves but for now we will do this hard coded
modules = ['activity', 'company', 'contact', 'custom_form',
	'examination', 'file', 'group', 'location', 'navigation', 'page',
	'pimpy', 'requirement', 'survey', 'upload', 'user', 'vacancy']

for module in modules:
	group_permission = GroupPermission(module, group.id, 2);
	db.session.add(group_permission)
	db.session.commit()


activity_permission = GroupPermission('activity', group_all.id, 1)

db.session.add(activity_permission)
db.session.commit()

