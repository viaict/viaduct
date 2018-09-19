from app import app, Roles
from app.exceptions.base import ResourceNotFoundException, \
    AuthorizationException
from app.repository import custom_form_repository
from app.service import role_service, group_service
from app.utils import copernica


def find_form_by_form_id(form_id):
    return custom_form_repository.get_form_by_form_id(form_id)


def get_form_by_form_id(form_id):
    form = custom_form_repository.get_form_by_form_id(form_id)
    if not form:
        raise ResourceNotFoundException("custom form", form_id)
    return form


def get_inactive_forms_by_user(user):
    if role_service.user_has_role(user, Roles.FORM_ADMIN):
        return custom_form_repository.get_inactive_forms(group_ids=None)

    group_ids = [g.id for g in group_service.get_groups_for_user(user)]
    return custom_form_repository.get_inactive_forms(group_ids=group_ids)


def get_active_followed_forms_by_user(user):
    if role_service.user_has_role(user, Roles.FORM_ADMIN):
        return custom_form_repository. \
            get_active_followed_forms_by_user(user_id=user.id, group_ids=None)

    group_ids = [g.id for g in group_service.get_groups_for_user(user)]
    return custom_form_repository. \
        get_active_followed_forms_by_user(user_id=user.id, group_ids=group_ids)


def get_active_unfollowed_by_user(user):
    if role_service.user_has_role(user, Roles.FORM_ADMIN):
        return custom_form_repository. \
            get_active_unfollowed_by_user(user_id=user.id, group_ids=None)

    group_ids = [g.id for g in group_service.get_groups_for_user(user)]
    return custom_form_repository. \
        get_active_unfollowed_by_user(user_id=user.id, group_ids=group_ids)


def get_form_entries_by_form_id(form_id):
    return custom_form_repository.get_form_entries_by_form_id(form_id)


def get_form_submission_by_id(form_id, submission_id):
    submission = custom_form_repository. \
        get_form_submission_by_id(form_id, submission_id)
    if not submission:
        raise ResourceNotFoundException("custom form submission",
                                        submission_id)
    return submission


def find_form_submission_by_user_id(form_id, user_id):
    return custom_form_repository. \
        get_form_submission_by_user_id(form_id, user_id)


def find_form_following_by_user_id(form, user_id):
    return custom_form_repository. \
        get_form_following_by_user_id(form, user_id)


def toggle_form_follow(form_id, user_id):
    """
    Toggle the following of a form.

    :return: True if following, False if unfollowed.
    """
    form = get_form_by_form_id(form_id)

    follower = find_form_following_by_user_id(form=form, user_id=user_id)
    if follower:
        custom_form_repository.delete_form_follow(follower)
        return False
    else:
        custom_form_repository.follow_form(form=form, user_id=user_id)
        return True


def follow_form(form, user_id):
    custom_form_repository.follow_form(form=form, user_id=user_id)


def form_set_archive_status(form_id, archived):
    form = get_form_by_form_id(form_id)

    custom_form_repository.form_set_archive_status(form, archived)


def toggle_form_submission_paid(form_id, submission_id):
    submission = get_form_submission_by_id(form_id, submission_id)

    paid = not submission.has_paid

    custom_form_repository.form_set_paid_status(submission, paid)

    copernica_data = {
        "Betaald": "Ja" if submission.has_paid else "Nee",
    }

    copernica.update_subprofile(app.config['COPERNICA_ACTIVITEITEN'],
                                submission.owner_id, submission.form_id,
                                copernica_data)


def check_user_can_access_form(form_id, user):
    """Permission check for a user accessing a form."""

    # Probably a create function
    if form_id is None:
        return True

    if role_service.user_has_role(user, Roles.FORM_ADMIN):
        return True

    form = get_form_by_form_id(form_id)
    user_groups = group_service.get_groups_for_user(user)

    if form.group is not None and form.group in user_groups:
        return True

    error = "User has no form admin role and is not member of form's group"
    raise AuthorizationException(error)


def get_available_owner_groups_for_user(user):
    if role_service.user_has_role(user, Roles.FORM_ADMIN):
        return group_service.find_groups()
    else:
        return group_service.get_groups_for_user(user)
