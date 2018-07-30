import bcrypt
from flask_babel import _

from app.exceptions import ResourceNotFoundException, ValidationException, \
    AuthorizationException, BusinessRuleException
from app.repository import user_repository
from app.service import file_service, mail_service
from app.enums import FileCategory
from app.utils import copernica


def set_password(user_id, password):
    """Set the new password for user with id."""
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    user = get_user_by_id(user_id)
    user.password = password
    user_repository.save(user)
    return user


def find_user_by_email(email):
    """Retrieve the user by email or return None."""
    return user_repository.find_user_by_email(email)


def get_user_by_email(email):
    """Retrieve the user by email, throw error if not found."""
    user = find_user_by_email(email)
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
    return user_repository.find_user_by_student_id(student_id)


def get_user_by_student_id(student_id):
    """Retrieve the user by student id, throw error if not found."""
    user = find_user_by_student_id(student_id)
    if not user:
        raise ResourceNotFoundException("user", student_id)

    return user


def set_confirmed_student_id(user, student_id):
    # Check if there is not another account with the same student ID
    # that is already confirmed

    other_user = find_user_by_student_id(student_id)
    if other_user is not None:
        raise BusinessRuleException("Student ID already linked to other user.")

    # Find all users with the same student ID (unconfirmed)
    # and set it to None
    other_users = user_repository.find_all_users_with_unconfirmed_student_id(
        student_id)

    for user in other_users:
        user.student_id = None

    # Set the confirmed student ID of the user
    user.student_id = student_id
    user.student_id_confirmed = True

    # Save everything at once
    user_repository.save_all(other_users + [user])


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


def register_new_user(email, password, first_name, last_name, student_id,
                      education_id, birth_date, study_start,
                      receive_information, phone_nr, address,
                      zip_, city, country, locale, link_student_id=False):

    if find_user_by_email(email) is not None:
        raise BusinessRuleException(
            'A user with the same email address already exists.')

    user = user_repository.create_user()

    user.email = email

    user.password = bcrypt.hashpw(password, bcrypt.gensalt())
    user.first_name = first_name
    user.last_name = last_name
    user.student_id = student_id
    user.education_id = education_id
    user.birth_date = birth_date
    user.study_start = study_start
    user.receive_information = receive_information
    user.phone_nr = phone_nr
    user.address = address
    user.zip = zip_
    user.city = city
    user.country = country
    user.locale = locale

    users = [user]

    if link_student_id:
        user.student_id_confirmed = True
        unconfirmed_users = user_repository. \
            find_all_users_with_unconfirmed_student_id(user.student_id)

        for u in unconfirmed_users:
            u.student_id = None
            users.append(u)

    user_repository.save_all(users)

    copernica.update_user(user)

    if locale == 'nl':
        mail_template = 'email/sign_up_nl.html'
    else:
        mail_template = 'email/sign_up_en.html'

    mail_service.send_mail(
        user.email, _('Welcome to via, %(name)s', name=user.first_name),
        mail_template, user=user)

    return user
