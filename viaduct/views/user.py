# -*- coding: utf-8 -*-
import bcrypt
import random
import datetime
import smtplib
from unicodecsv import writer
from StringIO import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import flash, redirect, render_template, request, url_for, abort,\
    session
from flask import Blueprint
from flask.ext.login import current_user, login_user, logout_user

from sqlalchemy import or_


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
                  'the e-mail address specified does already exist.', 'error')
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
                  'the e-mail address specified does already exist.', 'error')
            return render_template('user/sign_up.htm', form=form)

        user = User(form.email.data, bcrypt.hashpw(form.password.data,
                    bcrypt.gensalt()), form.first_name.data,
                    form.last_name.data, form.student_id.data,
                    form.education_id.data)

        exists = User.query.filter(User.email == user.email)

        if exists:
            db.session.add(user)
            db.session.commit()

            group = Group.query.filter(Group.name == 'all').first()
            group.add_user(user)

            db.session.add(group)
            db.session.commit()

            #Upload avatar
            UserAPI.upload(request.files['avatar'], user.id)

            #user.add_to_all()

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

        flash('You\'ve been signed in successfully.', 'succes')

        denied_from = session.get('denied_from')
        if denied_from:
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

    if 'denied_from' in session:
        session['denied_from'] = None

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
            flash('De ingevoerde gegevens zijn niet correct.', 'error')
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
                    flash('De ingevoerde gegevens zijn niet correct.', 'error')

                # Actually reset the password of the user
                user.password = bcrypt.hashpw(
                    form.password.data, bcrypt.gensalt())

                db.session.add(user)
                db.session.commit()

                flash('Uw wachtwoord is aangepast', 'success')
        else:
            flash('Ongeldige password-reset ticket', 'error')

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
@blueprint.route('/users/<int:page_nr>/', methods=['GET', 'POST'])
def view(page_nr=1):
    #if not current_user.has_permission('user.view'):
    #   abort(403)
    if not GroupPermissionAPI.can_read('user'):
        return abort(403)

    # persumably, if the method is a post we have selected stuff to delete,
    # similary to groups.
    if request.method == 'POST':
        user_ids = request.form.getlist('select')

        del_users = User.query.filter(User.id.in_(user_ids)).all()

        for user in del_users:
            db.session.delete(user)

        db.session.commit()

        if len(del_users) > 1:
            flash('The selected users have been deleted.', 'success')
        else:
            flash('The selected user has been deleted.', 'success')

        redirect(url_for('user.view'))

    search = ''
    vvv = ''
    member = 'nocare'

    # Get a list of users to render for the current page.
    users = User.query

    if request.args.get('search'):
        search = request.args.get('search')
        searches = search.split(' ')

        for s in searches:
            if not s:
                continue

            users = users\
                .filter(or_(User.first_name.like('%' + s + '%'),
                            User.last_name.like('%' + s + '%'),
                            User.email.like('%' + s + '%'),
                            User.student_id.like('%' + s + '%')))

    if request.args.get('vvv') and request.args.get('vvv') == 'on':
        vvv = 'on'
        users = users.filter(User.favourer == True)  # noqa

    member_set = request.args.get('member')

    if member_set in ['nocare', 'yes', 'no']:
        member = member_set

        if member == 'yes':
            users = users.filter(User.has_payed == True)  # noqa
        elif member == 'no':
            users = users.filter(or_(User.has_payed == False,
                                     User.has_payed == None))  # noqa

    users = users\
        .order_by(User.first_name)\
        .order_by(User.last_name)\
        .paginate(page_nr, 15, False)

    return render_template('user/view.htm', users=users, search=search,
                           vvv=vvv, member=member)


@blueprint.route('/users/export', methods=['GET'])
def user_export():
    #if not current_user.has_permission('user.view'):
    #   abort(403)
    if not GroupPermissionAPI.can_read('user'):
        return abort(403)

    users = User.query.all()
    si = StringIO()
    cw = writer(si)
    cw.writerow([c.name for c in User.__mapper__.columns])
    for user in users:
        cw.writerow([getattr(user, c.name) for c in User.__mapper__.columns])
    return si.getvalue().strip('\r\n')
