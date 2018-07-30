# -*- coding: utf-8 -*-
import json
import re
from csv import writer
from datetime import datetime
from io import StringIO

from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for, abort, \
    session
from flask_babel import _
from flask_login import current_user, login_user, logout_user, login_required

from app import db, login_manager, get_locale
from app.decorators import require_role, response_headers
from app.exceptions import ResourceNotFoundException, AuthorizationException, \
    ValidationException, BusinessRuleException
from app.forms.user import (EditUserForm, EditUserInfoForm, SignUpForm,
                            SignInForm, ResetPasswordForm, RequestPassword,
                            ChangePasswordForm, EditUvALinkingForm)
from app.models.activity import Activity
from app.models.custom_form import CustomFormResult, CustomForm
from app.models.education import Education
from app.models.user import User
from app.roles import Roles
from app.service import password_reset_service, user_service, \
    role_service, file_service, saml_service
from app.utils import copernica
from app.utils.google import HttpError
from app.utils.user import UserAPI

blueprint = Blueprint('user', __name__)


@login_manager.user_loader
def load_user(user_id):
    # The hook used by the login manager to get the user from the database by
    # user ID.
    return user_service.get_user_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(
        url_for("user.sign_in",
                next=url_for("oauth.authorize", **request.args)))


@blueprint.route('/users/view/', methods=['GET'])
@blueprint.route('/users/view/<int:user_id>', methods=['GET'])
@login_required
def view_single(user_id=None):
    if user_id is None:
        if current_user.is_authenticated:
            return redirect(url_for('user.view_single',
                                    user_id=current_user.id))
        return redirect(url_for('user.view'))

    can_read = False
    can_write = False

    # Unpaid members cannot view other profiles
    if current_user.id != user_id and not current_user.has_paid:
        return abort(403)
    # A user can always view his own profile
    if current_user.id == user_id:
        can_write = True
        can_read = True
    # group rights
    if role_service.user_has_role(current_user, Roles.USER_READ):
        can_read = True
    if role_service.user_has_role(current_user, Roles.USER_WRITE):
        can_write = True
        can_read = True

    user = user_service.get_user_by_id(user_id)
    user.avatar = UserAPI.avatar(user)
    user.groups = UserAPI.get_groups_for_user_id(user)

    user.groups_amount = len(user.groups)

    if "gravatar" in user.avatar:
        user.avatar = user.avatar + "&s=341"

    # Get all activity entrees from these forms, order by start_time of
    # activity.
    activities = Activity.query.join(CustomForm).join(CustomFormResult). \
        filter(CustomFormResult.owner_id == user_id and
               CustomForm.id == CustomFormResult.form_id and
               Activity.form_id == CustomForm.id)

    user.activities_amount = activities.count()

    new_activities = activities \
        .filter(Activity.end_time > datetime.today()).distinct() \
        .order_by(Activity.start_time)
    old_activities = activities \
        .filter(Activity.end_time < datetime.today()).distinct() \
        .order_by(Activity.start_time.desc())

    return render_template('user/view_single.htm', user=user,
                           new_activities=new_activities,
                           old_activities=old_activities,
                           can_read=can_read,
                           can_write=can_write)


@blueprint.route('/users/remove_avatar/<int:user_id>', methods=['DELETE'])
@login_required
@require_role(Roles.USER_WRITE)
def remove_avatar(user_id=None):
    user = user_service.get_user_by_id(user_id)
    if current_user.is_anonymous or current_user.id != user_id:
        return "", 403

    user_service.remove_avatar(user.id)
    return "", 200


@blueprint.route('/users/create/', methods=['GET', 'POST'])
@blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id=None):
    """Create user for admins and edit for admins and users."""

    # TODO: Split the edit my own user and edit other user routes.
    # We cannot check the rights using the decorator because normal
    # users also change their profile using this route.

    if (user_id is not None and current_user.id != user_id and
            not role_service.user_has_role(current_user, Roles.USER_WRITE)):
        abort(403)

    # Select user
    if user_id:
        user = user_service.get_user_by_id(user_id)
    else:
        user = User()

    user.avatar = user_service.user_has_avatar(user_id)

    if role_service.user_has_role(current_user, Roles.USER_WRITE):
        form = EditUserForm(request.form, obj=user)
        is_admin = True
    else:
        form = EditUserInfoForm(request.form, obj=user)
        is_admin = False

    form.new_user = user.id == 0

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    def edit_page():
        return render_template('user/edit.htm', form=form, user=user,
                               is_admin=is_admin)

    if form.validate_on_submit():

        # Only new users need a unique email.
        query = User.query.filter(User.email == form.email.data)
        if user_id:
            query = query.filter(User.id != user_id)

        if query.count() > 0:
            flash(_('A user with this e-mail address already exist.'),
                  'danger')
            return edit_page()

        # Because the user model is constructed to have an ID of 0 when it is
        # initialized without an email adress provided, reinitialize the user
        # with a default string for email adress, so that it will get a unique
        # ID when committed to the database.
        if not user_id:
            user = User('_')

        try:
            user.update_email(form.email.data.strip())
        except HttpError as e:
            if e.resp.status == 404:
                flash(_('According to Google this email does not exist. '
                        'Please use an email that does.'), 'danger')
                return edit_page()
            raise e

        user.first_name = form.first_name.data.strip()
        user.last_name = form.last_name.data.strip()
        user.locale = form.locale.data
        if role_service.user_has_role(current_user, Roles.USER_WRITE):
            user.has_paid = form.has_paid.data
            user.honorary_member = form.honorary_member.data
            user.favourer = form.favourer.data
            user.disabled = form.disabled.data
            user.alumnus = form.alumnus.data
        user.student_id = form.student_id.data.strip()
        user.education_id = form.education_id.data
        user.birth_date = form.birth_date.data
        user.study_start = form.study_start.data
        user.receive_information = form.receive_information.data

        user.phone_nr = form.phone_nr.data.strip()
        user.address = form.address.data.strip()
        user.zip = form.zip.data.strip()
        user.city = form.city.data.strip()
        user.country = form.country.data.strip()

        db.session.add(user)
        db.session.commit()

        avatar = request.files['avatar']
        if avatar:
            UserAPI.upload(avatar, user.id)

        if user_id:
            copernica.update_user(user)
            flash(_('Profile succesfully updated'))
        else:
            copernica.update_user(user, subscribe=True)
            flash(_('Profile succesfully created'))
        return redirect(url_for('user.view_single', user_id=user.id))

    return edit_page()


@blueprint.route('/users/edit/<int:user_id>/student-id-linking',
                 methods=['GET', 'POST'])
@login_required
@require_role(Roles.USER_WRITE)
def edit_student_id_linking(user_id):
    user = user_service.get_user_by_id(user_id)

    form = EditUvALinkingForm(request.form, obj=user)

    def edit_page():
        return render_template('user/edit_student_id.htm',
                               user=user, form=form)

    if form.validate_on_submit():

        if not form.student_id.data:
            user_service.remove_student_id(user)
        elif form.student_id_confirmed.data:
            other_user = user_service.find_user_by_student_id(
                form.student_id.data)

            if other_user:
                error = _('The UvA account corresponding with this student ID '
                          'is already linked to another user '
                          '(%(name)s - %(email)s). Please unlink the account '
                          'from the other user first before linking it '
                          'to this user.', name=other_user.name,
                          email=other_user.email)

                form.student_id_confirmed.errors.append(error)

                return edit_page()

            user_service.set_confirmed_student_id(user, form.student_id.data)
        else:
            user_service.set_unconfirmed_student_id(user, form.student_id.data)

        flash(_('Student ID information saved.'), 'success')

        return redirect(url_for('.edit', user_id=user_id))

    return edit_page()


@blueprint.route('/sign-up/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def sign_up():
    return render_template('user/sign_up_chooser.htm')


@blueprint.route('/sign-up/manual/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def sign_up_manual():
    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = SignUpForm(request.form)

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    if form.validate_on_submit():
        try:
            user = user_service.register_new_user(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                student_id=form.student_id.data,
                education_id=form.education_id.data,
                birth_date=form.birth_date.data,
                study_start=form.study_start.data,
                receive_information=form.receive_information.data,
                phone_nr=form.phone_nr.data,
                address=form.address.data,
                zip_=form.zip.data,
                city=form.city.data,
                country=form.country.data,
                locale=get_locale())

            login_user(user)

            flash(_('Welcome %(name)s! Your profile has been succesfully '
                    'created and you have been logged in!',
                    name=current_user.first_name), 'success')

            return redirect(url_for('home.home'))

        except BusinessRuleException:
            flash(_('A user with this e-mail address already exists'),
                  'danger')

    return render_template('user/sign_up.htm', form=form)


@blueprint.route('/sign-up/process-saml-response/', methods=['GET', 'POST'])
@saml_service.ensure_data_cleared
def sign_up_saml_response():
    redir_url = saml_service.get_redirect_url(url_for('home.home'))

    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user.is_authenticated:

        # End the sign up session when it is still there somehow
        if saml_service.sign_up_session_active():
            saml_service.end_sign_up_session()

        return redirect(redir_url)

    if saml_service.sign_up_session_active():

        # Delete the old sign up session when
        # the user re-authenticates
        if saml_service.user_is_authenticated():
            saml_service.end_sign_up_session()

        # Otherwise, refresh the timeout timestamp of the session
        else:
            saml_service.update_sign_up_session_timestamp()

    form = SignUpForm(request.form)

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    if not saml_service.sign_up_session_active():

        if not saml_service.user_is_authenticated():
            flash(_('Authentication failed. Please try again.'), 'danger')
            return redirect(redir_url)

        if not saml_service.user_is_student():
            flash(_('You must authenticate with a student '
                  'UvA account to register.'), 'danger')
            return redirect(redir_url)

        if saml_service.uid_is_linked_to_other_user():
            flash(_('There is already an account linked to this UvA account. '
                    'If you are sure that this is a mistake please send '
                    'an email to the board.'), 'danger')
            return redirect(redir_url)

        # Start a new sign up session and pre-fill the form
        saml_service.start_sign_up_session()
        saml_service.fill_sign_up_form_with_saml_attributes(
            form)

    # When we encounter a GET request but a session is already active,
    # this means that the user did a refresh without submitting the form.
    # We redirect him/her to the SAML sign up, since otherwise all
    # pre-filled data would be gone.
    elif request.method == 'GET':
        return redirect(url_for('saml.sign_up'))

    else:
        # Make sure that it is not possible to change the student id
        form.student_id.data = \
            saml_service.get_sign_up_session_linking_student_id()

    if form.validate_on_submit():
        try:
            user = user_service.register_new_user(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                student_id=form.student_id.data,
                education_id=form.education_id.data,
                birth_date=form.birth_date.data,
                study_start=form.study_start.data,
                receive_information=form.receive_information.data,
                phone_nr=form.phone_nr.data,
                address=form.address.data,
                zip_=form.zip.data,
                city=form.city.data,
                country=form.country.data,
                locale=get_locale(),
                link_student_id=True)

            login_user(user)

            saml_service.end_sign_up_session()

            flash(_('Welcome %(name)s! Your profile has been succesfully '
                    'created and you have been logged in!',
                    name=current_user.first_name), 'success')

            return redirect(redir_url)

        except BusinessRuleException:
            flash(_('A user with this e-mail address already exists'),
                  'danger')

    return render_template('user/sign_up.htm', form=form,
                           disable_student_id=True)


@blueprint.route('/sign-in/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def sign_in():
    # Redirect the user to the index page if he or she has been authenticated
    # already.

    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = SignInForm(request.form)

    if form.validate_on_submit():

        try:
            user = user_service.get_user_by_login(form.email.data,
                                                  form.password.data)

            # Notify the login manager that the user has been signed in.
            login_user(user)

            next_ = request.args.get("next", '')
            if next_ and next_.startswith("/"):
                return redirect(next_)

            # If referer is empty for some reason (browser policy, user entered
            # address in address bar, etc.), use empty string
            referer = request.headers.get('Referer', '')

            denied = (
                re.match(r'(?:https?://[^/]+)%s$' % (url_for('user.sign_in')),
                         referer) is not None)
            denied_from = session.get('denied_from')

            if not denied:
                if referer:
                    return redirect(referer)
            elif denied_from:
                return redirect(denied_from)

            return redirect(url_for('home.home'))

        except ResourceNotFoundException:
            flash(_(
                'It appears that account does not exist. Try again, or contact'
                ' the website administration at ict (at) svia (dot) nl.'))
        except AuthorizationException:
            flash(_('Your account has been disabled, you are not allowed '
                    'to log in'), 'danger')
        except ValidationException:
            flash(_('The password you entered appears to be incorrect.'))

    return render_template('user/sign_in.htm', form=form)


@blueprint.route('/sign-in/process-saml-response/', methods=['GET'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
@saml_service.ensure_data_cleared
def sign_in_saml_response():
    redir_url = saml_service.get_redirect_url(url_for('home.home'))

    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user.is_authenticated:
        return redirect(redir_url)

    if not saml_service.user_is_authenticated():
        flash(_('Authentication failed. Please try again.'), 'danger')
        return redirect(redir_url)

    try:
        user = saml_service.get_user_by_uid()
        login_user(user)

    except (ResourceNotFoundException, ValidationException):
        flash(_('There is no via account linked to this UvA account. '
                'You must link your via-account by confirming your student ID '
                'before you can log in with your UvA-net ID.'), 'danger')

    return redirect(redir_url)


@blueprint.route('/sign-out/')
def sign_out():
    # Notify the login manager that the user has been signed out.
    logout_user()

    flash(_('Captain\'s log succesfully ended.'), 'success')

    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)

    return redirect(url_for('home.home'))


@blueprint.route('/process-account-linking')
@saml_service.ensure_data_cleared
def process_account_linking_saml_response():
    redir_url = saml_service.get_redirect_url(url_for('home.home'))

    # Check whether a user is linking his/her own account
    # or an someone is linking another account
    linking_current_user = saml_service.is_linking_user_current_user()

    if not current_user.is_authenticated:
        if linking_current_user:
            flash(_('You need to be logged in to link your account.'),
                  'danger')
        else:
            flash(_('You need to be logged in to link an account.'), 'danger')

        return redirect(redir_url)

    if not saml_service.user_is_authenticated():
        flash(_('Authentication failed. Please try again.'), 'danger')
        return redirect(redir_url)

    if linking_current_user:
        try:
            saml_service.link_uid_to_user(current_user)
            flash(_('Your account is now linked to this UvA account.'),
                  'success')
        except BusinessRuleException:
            flash(_('There is already an account linked to this UvA account. '
                    'If you are sure that this is a mistake please send '
                    'an email to the board.'), 'danger')
    else:
        try:
            link_user = saml_service.get_linking_user()
            saml_service.link_uid_to_user(link_user)

            flash(_('The account is now linked to this UvA account.'),
                  'success')
        except BusinessRuleException:
            flash(_('There is already an account linked to this UvA account.'),
                  'danger')
        except ResourceNotFoundException:
            # Should not happen normally
            flash(_('Could not find the user to link this UvA account to.'),
                  'danger')

    return redirect(redir_url)


@blueprint.route('/request_password/', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def request_password():
    """Create a ticket and send a email with link to reset_password page."""
    if current_user.is_authenticated:
        return redirect(url_for('user.view_single', user_id=current_user.id))

    form = RequestPassword(request.form)

    if form.validate_on_submit():
        try:
            password_reset_service.create_password_ticket(form.email.data)
            flash(_('An email has been sent to %(email)s with further '
                    'instructions.', email=form.email.data), 'success')
            return redirect(url_for('home.home'))

        except ResourceNotFoundException:
            flash(_('%(email)s is unknown to our system.',
                    email=form.email.data), 'danger')

    return render_template('user/request_password.htm', form=form)


@blueprint.route('/reset_password/<string:hash_>', methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def reset_password(hash_):
    """
    Reset form existing of two fields, password and password_repeat.

    Checks if the hash in the url is found in the database and timestamp
    has not expired.
    """
    try:
        ticket = password_reset_service.get_valid_ticket(hash_)
    except ResourceNotFoundException:
        flash(_('No valid ticket found'), 'danger')
        return redirect(url_for('user.request_password'))

    form = ResetPasswordForm(request.form)

    if form.validate_on_submit():
        password_reset_service.reset_password(ticket, form.password.data)
        flash(_('Your password has been updated.'), 'success')
        return redirect(url_for('user.sign_in'))

    return render_template('user/reset_password.htm', form=form)


@blueprint.route("/users/<int:user_id>/password/", methods=['GET', 'POST'])
@response_headers({"X-Frame-Options": "SAMEORIGIN"})
def change_password(user_id):
    if (user_id is not None and current_user.id != user_id and
            not role_service.user_has_role(current_user, Roles.USER_WRITE)):
        abort(403)

    form = ChangePasswordForm()

    if form.validate_on_submit():
        if user_service.validate_password(current_user,
                                          form.current_password.data):
            user_service.set_password(current_user.id,
                                      form.password.data)
            flash(_("Your password has successfully been changed."))
            return redirect(url_for("home.home"))
        else:
            form.current_password.errors.append(
                _("Your current password does not match."))
    return render_template("user/change_password.htm", form=form)


@blueprint.route('/users/', methods=['GET', 'POST'])
@require_role(Roles.USER_READ)
def view():
    return render_template('user/view.htm')


@blueprint.route('/users/export', methods=['GET'])
@require_role(Roles.USER_READ)
def user_export():
    users = User.query.all()
    si = StringIO()
    cw = writer(si)
    cw.writerow([c.name for c in User.__mapper__.columns])
    for user in users:
        cw.writerow([getattr(user, c.name) for c in User.__mapper__.columns])
    return si.getvalue().strip('\r\n')


@blueprint.route('/users/avatar/<int:user_id>/', methods=['GET'])
@login_required
def view_avatar(user_id=None):
    can_read = False

    # Unpaid members cannot view other avatars
    if current_user.id != user_id and not current_user.has_paid:
        return abort(403)

    # A user can always view his own avatar
    if current_user.id == user_id:
        can_read = True

    # group rights
    if role_service.user_has_role(current_user, Roles.USER_READ) \
            or role_service.user_has_role(current_user, Roles.USER_WRITE) \
            or role_service.user_has_role(current_user, Roles.ACTIVITY_WRITE):
        can_read = True

    if not can_read:
        return abort(403)

    if not user_service.user_has_avatar(user_id):
        return abort(404)

    user = user_service.get_user_by_id(user_id)

    avatar_file = file_service.get_file_by_id(user.avatar_file_id)

    fn = 'user_avatar_' + str(user.id)

    content = file_service.get_file_content(avatar_file)
    headers = file_service.get_file_content_headers(
        avatar_file, display_name=fn)

    return content, headers


###
# Here starts the public api for users
###
@blueprint.route('/users/get_users/', methods=['GET'])
@require_role(Roles.USER_READ)
def get_users():
    users = User.query.all()
    user_list = []

    for user in users:
        user_list.append(
            [user.id,
             user.email,
             user.first_name,
             user.last_name,
             user.student_id,
             user.education.name
             if user.education else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.has_paid else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.honorary_member else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.favourer else "",
             "<i class='glyphicon glyphicon-ok'></i>"
             if user.alumnus else ""
             ])
    return json.dumps({"data": user_list})
