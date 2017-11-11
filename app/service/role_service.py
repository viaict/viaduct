from flask_login import current_user

from app import app
from app.repository import role_repository


def user_has_role(user, *roles):
    return all(role.value in user.roles for role in roles)


@app.before_request
def load_user_roles():
    current_user.roles = [role.role for role in
                          role_repository.load_user_roles(current_user.id)]
