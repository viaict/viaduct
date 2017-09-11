from flask_login import current_user

from app import app
from app.repository import role_repository
from app.roles import Roles


def user_has_role(user, role):
    return role in user.roles


@app.before_request
def load_user_roles():
    current_user.roles = [Roles(role[0]) for role in
                          role_repository.load_user_roles(current_user.id)]
