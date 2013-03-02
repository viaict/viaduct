import bcrypt

from application import db
from application.user.models import User
from application.group.models import Group

# Create the database.
db.create_all()

# Add the administrator.
user = User('administrator', bcrypt.hashpw('administrator', bcrypt.gensalt()),
	'Administrator', '')

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

