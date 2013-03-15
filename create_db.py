import bcrypt

import datetime
from viaduct import db
from viaduct.user.models import User, UserPermission
from viaduct.group.models import Group, GroupPermission
from viaduct.page.models import Page, PagePermission
from viaduct.pimpy.models import Minute, Task

import os

# Remove the old db.
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

group = Group('anonymous')

db.session.add(group)
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



#	def __init__(self, title, content, deadline, group_id, users,
#				minute, line):

# Add standard pimpy tasks
minute = Minute("minute content, jaja", 2)
db.session.add(minute)
db.session.commit()

task = Task('test task', 'test content', datetime.date(2020, 10, 10), 2, [user], 1, minute.id)
db.session.add(task)
db.session.commit()
