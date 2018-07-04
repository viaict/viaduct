import bcrypt

from app.exceptions import ResourceNotFoundException, ValidationException, \
    AuthorizationException
from app.repository import user_repository
from app.service import file_service
from app.enums import FileCategory


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


def find_user_by_student_id(student_id):
    """Retrieve the user or return None."""
    user = user_repository.find_user_by_student_id(student_id)

    return user


def get_user_by_student_id(student_id):
    """Retrieve the user by student id, throw error if not found."""
    user = find_user_by_student_id(student_id)
    if not user:
        raise ResourceNotFoundException("user", student_id)

    return user


def clear_unconfirmed_student_id_in_all_users(student_id):
    users = user_repository.find_all_users_with_unconfirmed_student_id(
        student_id)

    for user in users:
        user.student_id = None
        user_repository.save(user)


def set_confirmed_student_id(user, student_id):
    # TODO: check if there is not another account with
    # the same confirmed student id
    # TODO: maybe merge with method above?

    user.student_id = student_id
    user.student_id_confirmed = True

    user_repository.save(user)


def set_unconfirmed_student_id(user, student_id):
    user.student_id = student_id
    user.student_id_confirmed = False

    user_repository.save(user)


def remove_student_id(user):
    user.student_id = None
    user.student_id_confirmed = False

    user_repository.save(user)


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


def user_has_avatar(user_id):
    user = get_user_by_id(user_id)

    return user.avatar_file_id is not None


def remove_avatar(user_id):
    user = get_user_by_id(user_id)

    _file = file_service.get_file_by_id(user.avatar_file_id)
    user.avatar_file_id = None

    user_repository.save(user)

    file_service.delete_file(_file)


def set_avatar(user_id, file_data):
    user = get_user_by_id(user_id)

    # Remove old avatar
    if user.avatar_file_id is not None:
        old_file = file_service.get_file_by_id(user.avatar_file_id)
        user.avatar_file_id = None
    else:
        old_file = None

    _file = file_service.add_file(FileCategory.USER_AVATAR,
                                  file_data, file_data.filename)

    user.avatar_file_id = _file.id

    if old_file:
        file_service.delete_file(old_file)

    user_repository.save(user)
