# -*- coding: utf-8 -*-
import json
import re
from csv import writer
from datetime import datetime
from io import StringIO

import bcrypt
from flask import Blueprint
from flask import flash, redirect, render_template, request, url_for, abort, \
    session
from flask_babel import _
from flask_login import current_user, login_user, logout_user, login_required

from app import db, login_manager
from app.exceptions import ResourceNotFoundException
from app.forms import SignUpForm, SignInForm, ResetPassword, RequestPassword
from app.forms.user import EditUserForm, EditUserInfoForm
from app.models.activity import Activity
from app.models.custom_form import CustomFormResult, CustomForm
from app.models.education import Education
from app.models.group import Group
from app.models.user import User
from app.service import password_reset_service
from app.utils import copernica
from app.utils.google import HttpError
from app.utils.module import ModuleAPI
from app.utils.user import UserAPI

blueprint = Blueprint('user', __name__)


@login_manager.user_loader
def load_user(user_id):
    # The hook used by the login manager to get the user from the database by
    # user ID.
    user = User.query.get(int(user_id))

    return user


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

    # Only logged in users can view profiles
    if current_user.is_anonymous:
        return abort(403)
    # Unpaid members cannot view other profiles
    if current_user.id != user_id and not current_user.has_paid:
        return abort(403)
    # A user can always view his own profile
    if current_user.id == user_id:
        can_write = True
        can_read = True
    # group rights
    if ModuleAPI.can_read('user'):
        can_read = True
    if ModuleAPI.can_write('user'):
        can_write = True
        can_read = True

    user = User.query.get_or_404(user_id)
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
def remove_avatar(user_id=None):
    user = User.query.get(user_id)
    if not ModuleAPI.can_write('user') and \
            (current_user.is_anonymous or current_user.id != user_id):
        return "", 403

    UserAPI.remove_avatar(user)
    return "", 200


@blueprint.route('/users/create/', methods=['GET', 'POST'])
@blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id=None):
    """Create user for admins and edit for admins and users."""
    if not ModuleAPI.can_write('user') and \
            (current_user.is_anonymous or current_user.id != user_id):
        return abort(403)

    # Select user
    if user_id:
        user = User.query.get_or_404(user_id)
    else:
        user = User()

    user.avatar = UserAPI.has_avatar(user_id)

    if ModuleAPI.can_write('user'):
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
            raise (e)

        user.first_name = form.first_name.data.strip()
        user.last_name = form.last_name.data.strip()
        user.locale = form.locale.data
        if ModuleAPI.can_write('user'):
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

        if form.password.data != '':
            user.password = bcrypt.hashpw(form.password.data, bcrypt.gensalt())

        group = Group.query.filter(Group.name == 'all').first()
        group.add_user(user)

        db.session.add(group)
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


@blueprint.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = SignUpForm(request.form)

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    if form.validate_on_submit():
        query = User.query.filter(User.email == form.email.data)

        if query.count() > 0:
            flash(_('A user with this e-mail address already exists'),
                  'danger')
            return render_template('user/sign_up.htm', form=form)

        user = User(form.email.data,
                    bcrypt.hashpw(form.password.data,
                                  bcrypt.gensalt()), form.first_name.data,
                    form.last_name.data, form.student_id.data,
                    form.education_id.data, form.birth_date.data,
                    form.study_start.data, form.receive_information.data)
        user.phone_nr = form.phone_nr.data
        user.address = form.address.data
        user.zip = form.zip.data
        user.city = form.city.data
        user.country = form.country.data

        group = Group.query.filter(Group.name == 'all').first()
        group.add_user(user)

        db.session.add(group)
        db.session.commit()

        db.session.add(user)
        db.session.commit()

        db.session.commit()

        copernica.update_user(user, subscribe=True)

        login_user(user)

        flash(_('Welcome %(name)s! Your profile has been succesfully '
                'created and you have been logged in!',
                name=current_user.first_name), 'success')

        return redirect(url_for('home.home'))

    return render_template('user/sign_up.htm', form=form)


@blueprint.route('/sign-in/', methods=['GET', 'POST'])
def sign_in():
    # Redirect the user to the index page if he or she has been authenticated
    # already.

    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = SignInForm(request.form)

    if form.validate_on_submit():
        user = form.validate_signin()

        if user:
            # Notify the login manager that the user has been signed in.
            login_user(user)
            if user.disabled:
                flash(_('Your account has been disabled, you are not allowed '
                        'to log in'), 'danger')
            else:
                flash(_('Hey %(name)s, you\'re now logged in!',
                        name=current_user.first_name), 'success')

            referer = request.headers.get('Referer')

            # If referer is empty for some reason (browser policy, user entered
            # address in address bar, etc.), use empty string
            if not referer:
                referer = ''

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

    return render_template('user/sign_in.htm', form=form)


@blueprint.route('/sign-out/')
def sign_out():
    # Notify the login manager that the user has been signed out.
    logout_user()

    flash(_('Captain\'s log succesfully ended.'), 'success')

    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)

    return redirect(url_for('home.home'))


@blueprint.route('/request_password/', methods=['GET', 'POST'])
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

    form = ResetPassword(request.form)

    if form.validate_on_submit():
        password_reset_service.reset_password(ticket, form.password.data)
        flash(_('Your password has been updated.'), 'success')
        return redirect(url_for('user.sign_in'))

    return render_template('user/reset_password.htm', form=form)


@blueprint.route('/users/', methods=['GET', 'POST'])
def view():
    if not ModuleAPI.can_read('user'):
        return abort(403)
    return render_template('user/view.htm')


@blueprint.route('/users/export', methods=['GET'])
def user_export():
    if not ModuleAPI.can_read('user'):
        return abort(403)

    users = User.query.all()
    si = StringIO()
    cw = writer(si)
    cw.writerow([c.name for c in User.__mapper__.columns])
    for user in users:
        cw.writerow([getattr(user, c.name) for c in User.__mapper__.columns])
    return si.getvalue().strip('\r\n')


###
# Here starts the public api for users
###
@blueprint.route('/users/get_users/', methods=['GET'])
def get_users():
    if not ModuleAPI.can_read('user'):
        return abort(403)

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


# Not used at the moment due to integrity problems in the database
@blueprint.route('/users/delete_users/', methods=['DELETE'])
def api_delete_user():
    if not ModuleAPI.can_write('user'):
        return abort(403)

    user_ids = request.get_json()['selected_ids']
    del_users = User.query.filter(User.id.in_(user_ids)).all()

    for user in del_users:
        db.session.delete(user)

    db.session.commit()

    return json.dumps({'status': 'success'})
