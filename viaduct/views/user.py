# -*- coding: utf-8 -*-
import bcrypt
import random
import datetime
import smtplib
import re
import json
from csv import writer
from io import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import flash, redirect, render_template, request, url_for, abort,\
    session
from flask import Blueprint
from flask.ext.login import current_user, login_user, logout_user

from viaduct import db, login_manager, application
from viaduct.helpers import flash_form_errors
from viaduct.forms import SignUpForm, SignInForm, ResetPassword,\
    RequestPassword
from viaduct.models import User
from viaduct.models.activity import Activity
from viaduct.models.custom_form import CustomFormResult, CustomForm
from viaduct.models.group import Group
from viaduct.models.request_ticket import Password_ticket
from viaduct.forms.user import EditUserForm, EditUserInfoForm
from viaduct.models.education import Education
from viaduct.api.group import GroupPermissionAPI
from viaduct.api import UserAPI

blueprint = Blueprint('user', __name__)


@login_manager.user_loader
def load_user(user_id):
    # The hook used by the login manager to get the user from the database by
    # user ID.
    user = User.query.get(int(user_id))

    return user


@blueprint.route('/users/view/<int:user_id>', methods=['GET'])
def view_single(user_id=None):
    if not GroupPermissionAPI.can_read('user') and\
            (not current_user or current_user.id != user_id):
        return abort(403)

    if not user_id:
        return abort(404)
    user = User.query.get(user_id)
    if not user:
        return abort(404)

    user.avatar = UserAPI.avatar(user)
    user.groups = UserAPI.get_groups_for_user_id(user)

    user.groups_amount = user.groups.count()

    if "gravatar" in user.avatar:
        user.avatar = user.avatar + "&s=341"

    # Get all activity entrees from these forms, order by start_time of
    # activity.
    activities = Activity.query.join(CustomForm).join(CustomFormResult).\
        filter(CustomFormResult.owner_id == user_id and
               CustomForm.id == CustomFormResult.form_id and
               Activity.form_id == CustomForm.id)

    user.activities_amount = activities.count()

    new_activities = activities\
        .filter(Activity.end_time > datetime.datetime.today()).distinct()\
        .order_by(Activity.start_time)
    old_activities = activities\
        .filter(Activity.end_time < datetime.datetime.today()).distinct()\
        .order_by(Activity.start_time.desc())

    return render_template('user/view_single.htm', user=user,
                           new_activities=new_activities,
                           old_activities=old_activities)


@blueprint.route('/users/remove_avatar/<int:user_id>', methods=['GET'])
def remove_avatar(user_id=None):
    user = User.query.get(user_id)
    if not GroupPermissionAPI.can_write('user') and\
            (not current_user or current_user.id != user_id):
        return abort(403)
    UserAPI.remove_avatar(user)
    return redirect(url_for('user.view_single', user_id=user_id))


@blueprint.route('/users/create/', methods=['GET', 'POST'])
@blueprint.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id=None):
    if not GroupPermissionAPI.can_write('user') and\
            (not current_user or current_user.id != user_id):
        return abort(403)

    # Select user
    if user_id:
        user = User.query.get(user_id)
    else:
        user = User()

    user.avatar = UserAPI.has_avatar(user_id)

    if GroupPermissionAPI.can_write('user'):
        form = EditUserForm(request.form, user)
        isAdmin = True
    else:
        form = EditUserInfoForm(request.form, user)
        isAdmin = False

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    if form.validate_on_submit():

        # Only new users need a unique email.
        query = User.query.filter(User.email == form.email.data)
        if user_id:
            query = query.filter(User.id != user_id)

        if query.count() > 0:
            flash('Een gebruiker met dit email adres bestaat al / A user with '
                  'the e-mail address specified does already exist.', 'danger')
            return render_template('user/edit.htm', form=form, user=user,
                                   isAdmin=isAdmin)

        # Because the user model is constructed to have an ID of 0 when it is
        # initialized without an email adress provided, reinitialize the user
        # with a default string for email adress, so that it will get a unique
        # ID when committed to the database.
        if not user_id:
            user = User('_')

        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.locale = form.locale.data
        if GroupPermissionAPI.can_write('user'):
            user.has_payed = form.has_payed.data
            user.honorary_member = form.honorary_member.data
            user.favourer = form.favourer.data
        user.student_id = form.student_id.data
        user.education_id = form.education_id.data
        user.birth_date = form.birth_date.data
        user.study_start = form.study_start.data

        if form.password.data != '':
            user.password = bcrypt.hashpw(form.password.data, bcrypt.gensalt())

        db.session.add(user)

        group = Group.query.filter(Group.name == 'all').first()
        group.add_user(user)

        db.session.add(group)
        db.session.commit()

        avatar = request.files['avatar']
        if avatar:
            UserAPI.upload(avatar, user.id)

        flash('The user has been %s successfully.' %
              ('edited' if user_id else 'created'), 'success')

        return redirect(url_for('user.view_single', user_id=user.id))
    else:
        flash_form_errors(form)

    return render_template('user/edit.htm', form=form, user=user,
                           isAdmin=isAdmin)


@blueprint.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user and current_user.is_authenticated():
        return redirect(url_for('home.home'))

    form = SignUpForm(request.form)

    # Add education.
    educations = Education.query.all()
    form.education_id.choices = [(e.id, e.name) for e in educations]

    if form.validate_on_submit():
        query = User.query.filter(User.email == form.email.data)

        if query.count() > 0:
            flash('Een gebruiker met dit email adres bestaat al / A user with '
                  'the e-mail address specified does already exist.', 'danger')
            return render_template('user/sign_up.htm', form=form)

        user = User(form.email.data, bcrypt.hashpw(form.password.data,
                    bcrypt.gensalt()), form.first_name.data,
                    form.last_name.data, form.student_id.data,
                    form.education_id.data, form.birth_date.data,
                    form.study_start.data)

        exists = User.query.filter(User.email == user.email)

        if exists:
            db.session.add(user)
            db.session.commit()

            group = Group.query.filter(Group.name == 'all').first()
            group.add_user(user)

            db.session.add(group)
            db.session.commit()

            # Upload avatar
            avatar = request.files['avatar']
            if avatar:
                UserAPI.upload(avatar, user.id)

            flash('You\'ve signed up successfully.', 'success')

        login_user(user)

        return redirect(url_for('home.home'))
    else:
        flash_form_errors(form)

    return render_template('user/sign_up.htm', form=form)


@blueprint.route('/sign-in/', methods=['GET', 'POST'])
def sign_in():
    # Redirect the user to the index page if he or she has been authenticated
    # already.
    if current_user and current_user.is_authenticated():
        return redirect(url_for('home.home'))

    form = SignInForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()

        if user is None:
            flash('It appears that account does not exist. Try again, or '
                  'contact the website administration at ict (at) svia (dot) '
                  'nl.', 'danger')
            return redirect(url_for('user.sign_in'))

        submitted_hash = bcrypt.hashpw(form.password.data, user.password)
        if submitted_hash != user.password:
            flash('The credentials that have been specified are invalid.',
                  'danger')
            return redirect(url_for('user.sign_in'))

        # Notify the login manager that the user has been signed in.
        login_user(user)

        flash('You\'ve been signed in successfully.', 'success')

        referer = request.headers.get('Referer')
        denied = re.match(r'(?:https?://[^/]+)%s$' % (url_for('user.sign_in')),
                          referer) is not None
        denied_from = session.get('denied_from')

        if not denied:
            if referer:
                return redirect(referer)
        elif denied_from:
            return redirect(denied_from)

        return redirect(url_for('home.home'))
    else:
        flash_form_errors(form)

    return render_template('user/sign_in.htm', form=form)


@blueprint.route('/sign-out/')
def sign_out():
    # Notify the login manager that the user has been signed out.
    logout_user()

    flash('You\'ve been signed out.', 'success')

    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)

    return redirect(url_for('home.home'))


@blueprint.route('/request_password/', methods=['GET', 'POST'])
def request_password():
    """ Create a ticket and send a email with link to reset_password page. """
    form = RequestPassword(request.form)

    if form.validate_on_submit():
        user = User.query.filter(
            User.email == form.email.data,
            User.student_id == form.student_id.data).first()

        # Check if the user does exist, and if the passwords do match.
        if not user:
            flash('De ingevoerde gegevens zijn niet correct.', 'danger')
        else:
            hash = create_hash(256)

            reset_link = "http://www.svia.nl" + url_for('user.reset_password')\
                + hash

            # Setup smtp trash
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Wachtwoord vergeten svia.nl'
            msg['From'] = application.config['GMAIL_MAIL_ACCOUNT']['username']
            msg['To'] = user.email

            mail_msg = MIMEText("""<h2>Wachtwoord vergeten link</h2><p>Iemand
                                heeft op svia.nl het wachtwoord voor het e-mail
                                adres %s geprobeerd te resetten. Als jij dit
                                bent, <a href="%s">Volg dan deze
                                link!</a></p><br><br><p>Groetjes</p>""" %
                                (user.email, reset_link), 'html')

            msg.attach(mail_msg)

            # Send mail to user with the following link.
            server = smtplib.SMTP("smtp.gmail.com:587")
            server.starttls()
            server.login(application.config['GMAIL_MAIL_ACCOUNT']['username'],
                         application.config['GMAIL_MAIL_ACCOUNT']['password'])
            server.sendmail(
                application.config['GMAIL_MAIL_ACCOUNT']['username'],
                user.email, msg.as_string())

            # Create validation ticket
            ticket = Password_ticket(user.id, hash)
            db.session.add(ticket)
            db.session.commit()

            flash('Er is een email verstuurd naar ' + form.email.data +
                  ' met instructies.', 'success')
    else:
        flash_form_errors(form)

    return render_template('user/request_password.htm', form=form)


@blueprint.route('/reset_password/', methods=['GET', 'POST'])
@blueprint.route('/reset_password/<string:hash>/', methods=['GET', 'POST'])
def reset_password(hash=0):
    """ Reset form existing of two fields, password and password_repeat.
    Checks if the hash in the url is found in the database and timestamp
    has not expired"""

    form = ResetPassword(request.form)

    if form.validate_on_submit():

        # Request the ticket to validate the timer
        ticket = Password_ticket.query.filter(
            Password_ticket.hash == hash).first()

        # Check if the request was followed within a hour
        if ticket:
            seconds = ((datetime.datetime.now() - ticket.created_on).seconds)
            if seconds < 3600:
                user = User.query.filter(User.id == ticket.user).first()

                # Check if the user does exist, and if the passwords do match.
                if not user:
                    flash('De ingevoerde gegevens zijn niet correct.',
                          'danger')

                # Actually reset the password of the user
                user.password = bcrypt.hashpw(
                    form.password.data, bcrypt.gensalt())

                db.session.add(user)
                db.session.commit()

                flash('Uw wachtwoord is aangepast', 'success')
        else:
            flash('Ongeldige password-reset ticket', 'danger')

    else:
        flash_form_errors(form)

    return render_template('user/reset_password.htm', form=form)


def create_hash(bits=96):
    assert bits % 8 == 0
    print("test")
    required_length = bits / 8 * 2
    s = hex(random.getrandbits(bits)).lstrip('0x').rstrip('L')
    if len(s) < required_length:
        return create_hash(bits)
    else:
        return s


@blueprint.route('/users/', methods=['GET', 'POST'])
def view():
    if not GroupPermissionAPI.can_read('user'):
        return abort(403)
    return render_template('user/view.htm')


@blueprint.route('/users/export', methods=['GET'])
def user_export():
    if not GroupPermissionAPI.can_read('user'):
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
    if not GroupPermissionAPI.can_read('user'):
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
                if user.has_payed else "",
             "<i class='glyphicon glyphicon-ok'></i>"
                if user.honorary_member else "",
             "<i class='glyphicon glyphicon-ok'></i>"
                if user.favourer else ""
             ])
    return json.dumps({"data": user_list})


# Not used at the moment due to integrity problems in the database
@blueprint.route('/users/delete_users/', methods=['DELETE'])
def api_delete_user():
    if not GroupPermissionAPI.can_write('user'):
        return abort(403)

    user_ids = request.json['selected_ids']
    del_users = User.query.filter(User.id.in_(user_ids)).all()

    for user in del_users:
        db.session.delete(user)

    db.session.commit()

    return json.dumps({'status': 'success'})
