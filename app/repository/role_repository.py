from app import db
from app.models.group import Group
from app.models.role_model import Role
from app.models.user import User


def load_user_roles(user_id):
    return db.session.query(Role).join(Role.groups, Group.users) \
        .filter(User.id == user_id).group_by(Role.role).all()
