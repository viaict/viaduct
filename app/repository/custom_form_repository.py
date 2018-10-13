from app import db
from app.models.activity import Activity
from app.models.custom_form import CustomFormFollower, CustomForm, \
    CustomFormResult

filter_unarchived = db.or_(CustomForm.archived == False,
                           CustomForm.archived == None)  # noqa
filter_active = db.or_(Activity.id == None,
                       db.and_(Activity.id != None,
                               db.func.now() < Activity.end_time))  # noqa

filter_archived_inactive = db.or_(CustomForm.archived == True,
                                  db.and_(Activity.id != None,
                                          db.func.now() >= Activity.end_time))  # noqa


def get_active_followed_forms_by_user(user_id, group_ids):
    """
    Get all forms followed by the user.

    Filter archived forms and forms with activities in the past.
    """
    q = db.session.query(CustomForm) \
        .outerjoin(Activity, CustomForm.id == Activity.form_id) \
        .filter(CustomFormFollower.query
                .filter(CustomForm.id == CustomFormFollower.form_id,
                        CustomFormFollower.owner_id == user_id)
                .exists(),
                filter_unarchived, filter_active)

    if group_ids is not None:
        q = q.filter(CustomForm.group_id.in_(group_ids))

    return q.order_by(CustomForm.id.desc()) \
        .all()


def get_active_unfollowed_by_user(user_id, group_ids):
    """
    Get all active forms not followed by the user.

    Filter archived forms and forms with activities in the past.
    """
    q = db.session.query(CustomForm) \
        .outerjoin(Activity, CustomForm.id == Activity.form_id) \
        .filter(db.not_(CustomFormFollower.query
                        .filter(CustomForm.id == CustomFormFollower.form_id,
                                CustomFormFollower.owner_id == user_id)
                        .exists()),
                filter_unarchived, filter_active)

    if group_ids is not None:
        q = q.filter(CustomForm.group_id.in_(group_ids))

    return q.order_by(CustomForm.id.desc()) \
        .all()


def get_inactive_forms(group_ids):
    """Get all inactive or ssarchived forms."""
    q = db.session.query(CustomForm) \
        .outerjoin(Activity, CustomForm.id == Activity.form_id) \
        .filter(filter_archived_inactive)

    if group_ids is not None:
        q = q.filter(CustomForm.group_id.in_(group_ids))

    return q.order_by(CustomForm.id.desc()) \
        .all()


def get_form_entries_by_form_id(form_id):
    return db.session.query(CustomFormResult) \
        .filter(CustomFormResult.form_id == form_id) \
        .order_by(CustomFormResult.created) \
        .all()


def get_form_by_form_id(form_id):
    return db.session.query(CustomForm) \
        .filter(CustomForm.id == form_id) \
        .one_or_none()


def get_form_submission_by_id(form_id, submit_id):
    return db.session.query(CustomFormResult) \
        .filter(CustomFormResult.id == submit_id,
                CustomFormResult.form_id == form_id) \
        .one_or_none()


def get_form_submission_by_user_id(form_id, user_id):
    return db.session.query(CustomFormResult) \
        .filter(CustomFormResult.owner_id == user_id,
                CustomFormResult.form_id == form_id) \
        .one_or_none()


def get_form_following_by_user_id(form, user_id):
    return db.session.query(CustomFormFollower) \
        .filter(CustomFormFollower.form == form,
                CustomFormFollower.owner_id == user_id) \
        .one_or_none()


def delete_form_follow(follower):
    print(follower)
    db.session.delete(follower)
    db.session.commit()


def follow_form(form, user_id):
    cf = CustomFormFollower(form=form, owner_id=user_id)
    db.session.add(cf)
    db.session.commit()


def form_set_archive_status(form, archived):
    form.archived = archived
    db.session.commit()


def form_set_paid_status(submission, paid):
    submission.has_paid = not submission.has_paid
    db.session.commit()
