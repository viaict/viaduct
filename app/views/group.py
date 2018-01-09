# coding: utf-8
import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import jsonify
from flask_login import current_user
from flask_babel import _

from app import db
from app.decorators import require_role
from app.forms.group import (ViewGroupForm, CreateGroupForm, EditGroupForm,
                             GroupRolesForm)
from app.models.group import Group
from app.models.user import User
from app.roles import Roles
from app.service import role_service, group_service
from app.utils import google

blueprint = Blueprint('group', __name__)


@blueprint.route('/groups/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:page_nr>/', methods=['GET', 'POST'])
@require_role(Roles.GROUP_READ)
def view(page_nr=1):
    form = ViewGroupForm(request.form)
    pagination = Group.query.order_by(Group.name).paginate(page_nr, 15, False)

    if form.validate_on_submit():
        if form.delete_group.data:
            if role_service.user_has_role(current_user, Roles.GROUP_WRITE):
                group_ids = []

                for group, form_entry in zip(pagination.items, form.entries):
                    if form_entry.select.data:
                        group_ids.append(group.id)

                groups = Group.query.filter(Group.id.in_(group_ids)).all()

                for group in groups:
                    db.session.delete(group)

                db.session.commit()

                if len(groups) > 1:
                    flash('The selected groups have been deleted.', 'success')
                else:
                    flash('The selected group has been deleted.', 'success')

                return redirect(url_for('group.view'))
            else:
                flash('This incident has been reported to our authorities.',
                      'warning')
    else:
        for group in pagination.items:
            form.entries.append_entry()

    can_write = role_service.user_has_role(current_user, Roles.GROUP_WRITE)

    return render_template('group/view.htm', form=form, pagination=pagination,
                           groups=zip(pagination.items, form.entries),
                           current_user=current_user, title='Groups',
                           can_write=can_write)


@blueprint.route('/groups/create/', methods=['GET', 'POST'])
@require_role(Roles.GROUP_WRITE)
def create():
    form = CreateGroupForm(request.form)

    if form.validate_on_submit():
        name = form.name.data.strip()
        mailtype = form.mailtype.data
        maillist = form.maillist.data.strip().lower()

        valid_form = True

        if Group.query.filter(Group.name == name).count() > 0:
            form.name.errors.append(
                _('There is already another group with this name.'))
            valid_form = False

        if mailtype != 'none' and Group.query.filter(
                Group.maillist == maillist).count() > 0:
            form.maillist.errors.append(
                _('There is already another group with this e-mail address.'))
            valid_form = False

        if valid_form:
            if maillist == '':
                group = Group(name, None)
            else:
                group = Group(name, maillist, mailtype)

            db.session.add(group)
            db.session.commit()

            # Only automatically create mailing lists
            if mailtype == 'mailinglist':
                google.create_group_if_not_exists(name, maillist)

            flash(_('The group has been created.'), 'success')

            if mailtype == 'mailbox':
                flash(_('Ask the board to create the mailbox for this'
                        ' group (if needed)'))

            return redirect(url_for('group.view'))

    return render_template('group/edit.htm', title=_('Create group'),
                           form=form)


@blueprint.route('/groups/<int:group_id>/edit/', methods=['GET', 'POST'])
@require_role(Roles.GROUP_WRITE)
def edit(group_id):
    group = Group.by_id(group_id)

    form = EditGroupForm(request.form, obj=group)

    if form.validate_on_submit():
        name = form.name.data.strip()
        mailtype = form.mailtype.data
        maillist = form.maillist.data.strip().lower()

        valid_form = True

        if Group.query.filter(Group.name == name,
                              Group.id != group_id).count() > 0:
            form.name.errors.append(
                _('There is already another group with this name.'))
            valid_form = False

        if mailtype != 'none' and Group.query.filter(
                Group.maillist == maillist,
                Group.id != group_id).count() > 0:
            form.maillist.errors.append(
                _('There is already another group with this e-mail address.'))
            valid_form = False

        if valid_form:
            group.name = name
            group.maillist = maillist
            if maillist == '' or mailtype == 'none':
                group.maillist = None
                group.mailtype = 'none'
            else:
                group.maillist = maillist
                group.mailtype = mailtype

            db.session.commit()

            # Only automatically create mailing lists
            if mailtype == 'mailinglist':
                google.create_group_if_not_exists(name, maillist)

            group.add_members_to_maillist()

            flash(_('The group has been edited.'), 'success')

            if mailtype == 'mailbox':
                flash(_('Ask the board to create the mailbox for this'
                        ' group (if needed)'))

            return redirect(url_for('group.view'))

    return render_template('group/edit.htm', title=_('Edit group'),
                           form=form, group=group)


@blueprint.route('/groups/<int:group_id>/users/', methods=['GET', 'POST'])
@require_role(Roles.GROUP_READ)
def view_users(group_id):
    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no such group.')
        return redirect(url_for('group.view'))

    users = group.users.order_by(User.first_name) \
        .order_by(User.last_name).all()

    return render_template('group/view_users.htm', group=group, users=users,
                           title='%s users' % (group.name))


@blueprint.route('/groups/<int:group_id>/get_users/', methods=['GET'])
@require_role(Roles.GROUP_READ)
def get_group_users(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if not group:
        flash('There is no such group.')
        return redirect(url_for('group.view'))

    users = group.users.all()

    user_list = [[user.id, user.name]
                 for user in users]
    user_list.sort()

    return json.dumps({"data": user_list})


@blueprint.route('/groups/<int:group_id>/delete_users/', methods=['DELETE'])
@require_role(Roles.GROUP_WRITE)
def delete_group_users(group_id):
    group = Group.query.filter(Group.id == group_id).first()
    if not group:
        flash('There is no such group.')
        return redirect(url_for('group.view'))

    user_ids = request.get_json()['selected_ids']

    users = group.get_users().filter(User.id.in_(user_ids)) \
        .order_by(User.first_name).order_by(User.last_name).all()

    for user in users:
        group.delete_user(user)

        db.session.add(group)
        db.session.commit()

    return json.dumps({'status': 'success'})


@blueprint.route('/groups/<int:group_id>/users/add/', methods=['GET', 'POST'])
@require_role(Roles.GROUP_WRITE)
def add_users(group_id, page_nr=1):
    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no such group.', 'danger')
        return redirect(url_for('group.view'))

    return render_template('group/add_users.htm',
                           group=group, title='Add users')


@blueprint.route("/groups/<int:group_id>/roles/", methods=['GET', 'POST'])
@require_role(Roles.GROUP_WRITE)
def roles(group_id):
    form = GroupRolesForm(request.form)
    form.roles.choices = role_service.find_all_roles()

    if form.validate_on_submit():
        role_service.set_roles_for_group(group_id, form.roles.data)

    form.roles.data = role_service.find_all_roles_by_group_id(group_id)
    group = group_service.get_group_by_id(group_id)
    return render_template("group/roles.htm", group=group, form=form)


@blueprint.route('/api/group/users/<int:group_id>/', methods=['GET'])
@require_role(Roles.GROUP_READ)
def group_api_get_users(group_id):
    group = Group.query.get(group_id)
    users = group.users.order_by(User.first_name, User.last_name).all()

    res = [{'val': user.id, 'label': user.name} for user in users]
    return jsonify(users=res)


@blueprint.route('/groups/<int:group_id>/users/add_users/', methods=['PUT'])
@require_role(Roles.GROUP_WRITE)
def group_api_add_users(group_id):
    group = Group.query.get(group_id)

    user_ids = request.get_json()['selected_ids']
    add_users = User.query.filter(User.id.in_(user_ids)).all()

    for user in add_users:
        group.add_user(user)

    db.session.add(group)
    db.session.commit()
    return "testestetsetset", 200
