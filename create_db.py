import bcrypt

from application import db
from application.user.models import User, UserPermission
from application.group.models import Group, GroupPermission
from application.page.models import Page, PagePermission

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

permissions = PagePermission(group, page, view=True)

db.session.add(permissions)
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

