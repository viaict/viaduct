import bcrypt

from app.exceptions import ResourceNotFoundException, ValidationException, \
    AuthorizationException
from app.repository import user_repository


def set_password(user_id, password):
    """Set the new password for user with id."""
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    user = get_user_by_id(user_id)
    user.password = password
    user_repository.save(user)
    return user


def get_user_by_email(email):
    """Retrieve the user by email, throw error if not found."""
    user = user_repository.find_user_by_email(email)
    if not user:
        raise ResourceNotFoundException("user", email)
    return user


def get_user_by_id(user_id):
    """Retrieve the user by id, throw error if not found."""
    user = find_by_id(user_id)
    if not user:
        raise ResourceNotFoundException('user', user_id)
    return user


def find_by_id(user_id):
    """Retrieve the user or return None."""
    return user_repository.find_by_id(user_id)


def find_members():
    """Find all users which are marked as member."""
    return user_repository.find_members()


def get_user_by_login(email, password):
    user = user_repository.find_user_by_email(email)
    if not user:
        raise ResourceNotFoundException('user', email)

    if user.disabled:
        raise AuthorizationException("User is disabled.")

    if not validate_password(user, password):
        raise ValidationException("Invalid password.")

    return user


def validate_password(user, password):  # type: (User, str) -> bool
    submitted_hash = bcrypt.hashpw(password, user.password)
    if submitted_hash == user.password:
        return True
    else:
        return False
