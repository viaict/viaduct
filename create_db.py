import bcrypt
import datetime
from viaduct import db
from viaduct.blueprints.user.models import User, UserPermission
from viaduct.blueprints.group.models import Group, GroupPermission
from viaduct.blueprints.page.models import Page, PagePermission, PageRevision
from viaduct.blueprints.pimpy.models import Minute, Task
from viaduct.models.navigation import NavigationEntry

import os

# Remove the old db.
if os.path.exists('application.db'):
	os.remove('application.db')

# Create the database.
db.create_all()

page = Page('')

db.session.add(page)
db.session.commit()

# Add the anonymous user.
user = User('anonymous', '', 'Anonymous', '')

db.session.add(user)
db.session.commit()

anon = Group('anonymous')

db.session.add(anon)
db.session.commit()

# Add the administrator.
user = User('administrator@svia.nl', bcrypt.hashpw('administrator',
		bcrypt.gensalt()), 'Administrator', '')

db.session.add(user)
db.session.commit()

# Add the administrators group.
group = Group('administrators')

db.session.add(group)
db.session.commit()

# Add the administrator to the administrators group.
group.add_user(user)

db.session.add(group)
db.session.commit()

# Grant the permissions.
permissions = UserPermission(group, view=True, create=True, edit=True,
	delete=True)

db.session.add(permissions)
db.session.commit()

permissions = GroupPermission(group, view=True, create=True, edit=True,
	delete=True)

db.session.add(permissions)
db.session.commit()

permissions = PagePermission(group, page, view=True, create=True, edit=True,
	delete=True)

db.session.add(permissions)
db.session.commit()


# Add stuff for pimpystuff for pimpy

user_maarten = User('maarten@maarten.mrt', 'pwd', 'Maarten', 'Inja')
user_ed = User('ed@ed.eds', 'pwd', 'Handsome', 'Ed')
group_first = Group('first')
group_second = Group('second')

# could I add more stuff at once?
db.session.add(user_maarten)
db.session.commit()
db.session.add(user_ed)
db.session.commit()
db.session.add(group_first)
db.session.commit()
db.session.add(group_second)
db.session.commit()

group_first.add_user(user_maarten)
group_first.add_user(user_ed)
group_first.add_user(user)
group_second.add_user(user_maarten)
group_second.add_user(user_ed)
group_second.add_user(user)

db.session.add(group_first)
db.session.commit()
db.session.add(group_second)
db.session.commit()


minute = Minute("minute content, jaja", 2)
db.session.add(minute)
db.session.commit()

# task
#	def __init__(self, title, content, deadline, group_id, users,
#				minute_id, line, status):

task0 = Task('test task', 'test content', datetime.date(2020, 10, 10), group_first.id, [user, user_maarten], 1, minute.id, 0)
db.session.add(task0)
db.session.commit()

task1 = Task('finish godamn pimpy', 'content', datetime.date(2015, 11, 9), group_second.id, [user, user_maarten, user_ed], 1, minute.id, 0)
db.session.add(task1)
db.session.commit()


task2 = Task('I dont even', 'sja', datetime.date(2017, 12, 15), group_second.id, [user_maarten, user_ed], 1, minute.id, 0)
db.session.add(task2)
db.session.commit()

# Do some pages.
page = Page('page1')
db.session.add(page)
db.session.commit()

permissions = PagePermission(group, page, view=True, create=True, edit=True,
		delete=True)
db.session.add(permissions)
db.session.commit()

permissions = PagePermission(anon, page, view=True, create=True, edit=True,
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

nav_activity = NavigationEntry(None, 'Activiteiten', '/activities', False, False, 4)
db.session.add(nav_activity)
db.session.commit()

nav_ext = NavigationEntry(nav_page1, 'Externaal', 'viaduct.svia.nl', True, False, 1)
db.session.add(nav_ext)
db.session.commit()

