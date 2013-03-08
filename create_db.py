import bcrypt

from viaduct import db
from viaduct.user.models import User, UserPermission
from viaduct.group.models import Group, GroupPermission
from viaduct.page.models import Page, PagePermission

# Create the database.
db.create_all()

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

