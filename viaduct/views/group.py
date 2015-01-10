# coding: utf-8

import copy
import pprint

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import abort, jsonify
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.utilities import serialize_sqla

from sqlalchemy import or_

from viaduct.api.group import GroupPermissionAPI

from viaduct.models import Group, GroupPermission, User
from viaduct.forms.group import EditGroupPermissionForm, ViewGroupForm

blueprint = Blueprint('group', __name__)


@blueprint.route('/groups/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:page_nr>/', methods=['GET', 'POST'])
def view(page_nr=1):
    if not(GroupPermissionAPI.can_read('group')):
        return abort(403)

    form = ViewGroupForm(request.form)
    pagination = Group.query.order_by(Group.name).paginate(page_nr, 15, False)

    if form.validate_on_submit():
        if form.delete_group.data:
            if GroupPermissionAPI.can_write('group'):
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

        flash_form_errors(form)

    return render_template('group/view.htm', form=form, pagination=pagination,
                           groups=zip(pagination.items, form.entries),
                           current_user=current_user, title='Groups')


@blueprint.route('/groups/create/', methods=['GET', 'POST'])
def create():
    if not(GroupPermissionAPI.can_write('group')):
        return abort(403)

    if request.method == 'POST':
        name = request.form['name'].strip()
        valid_form = True

        if not name:
            flash('No group name has been specified.', 'danger')
            valid_form = False
        elif Group.query.filter(Group.name == name).count() > 0:
            flash('The group name that has been specified is in use already.',
                  'danger')
            valid_form = False

        if valid_form:
            group = Group(name)

            db.session.add(group)
            db.session.commit()

            flash('The group has been created.', 'success')

            return redirect(url_for('group.view'))

    return render_template('group/create.htm', title='Create group')


@blueprint.route('/groups/<int:group_id>/users/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:group_id>/users/<int:page_nr>/',
                 methods=['GET', 'POST'])
def view_users(group_id, page_nr=1):
    if not(GroupPermissionAPI.can_read('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no such group.')
        return redirect(url_for('group.view'))

    if request.method == 'POST':
        user_ids = request.form.getlist('select')

        users = group.get_users().filter(User.id.in_(user_ids))\
            .order_by(User.first_name).order_by(User.last_name).all()

        for user in users:
            group.delete_user(user)

        db.session.add(group)
        db.session.commit()

        if len(user_ids) > 1:
            flash('The selected users have been deleted.', 'success')
        else:
            flash('The selected user has been deleted.', 'success')

        return redirect(url_for('group.view_users', group_id=group_id))

    if request.args.get('search'):
        search = request.args.get('search')
        users = group.get_users().\
            filter(or_(User.first_name.like('%' + search + '%'),
                       User.last_name.like('%' + search + '%'),
                       User.email.like('%' + search + '%'),
                       User.student_id.like('%' + search + '%')))\
            .order_by(User.first_name).order_by(User.last_name)\
            .paginate(page_nr, 15, False)
        return render_template('group/view_users.htm', group=group,
                               users=users, search=search,
                               title='%s users' % (group.name))

    users = group.get_users().order_by(User.first_name)\
        .order_by(User.last_name).paginate(page_nr, 15, False)

    return render_template('group/view_users.htm', group=group, users=users,
                           title='%s users' % (group.name))


@blueprint.route('/groups/<int:group_id>/users/add/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:group_id>/users/add/<int:page_nr>',
                 methods=['GET', 'POST'])
def add_users(group_id, page_nr=1):
    if not(GroupPermissionAPI.can_write('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no such group.', 'danger')
        return redirect(url_for('group.view'))

    if request.method == 'POST':
        user_ids = request.form.getlist('select')

        users = User.query.filter(User.id.in_(user_ids))\
            .order_by(User.first_name).order_by(User.last_name).all()

        for user in users:
            group.add_user(user)

        db.session.add(group)
        db.session.commit()

        if len(user_ids) > 1:
            flash('The selected users have been added to the group.',
                  'success')
        else:
            flash('The selected user has been added to the group.', 'success')

        return redirect(url_for('group.view_users', group_id=group_id))

    if request.args.get('search'):
        search = request.args.get('search')
        users = User.query.\
            filter(or_(User.first_name.like('%' + search + '%'),
                       User.last_name.like('%' + search + '%'),
                       User.email.like('%' + search + '%'),
                       User.student_id.like('%' + search + '%')))\
            .order_by(User.last_name).paginate(page_nr, 15, False)
        return render_template('group/add_users.htm', group=group, users=users,
                               search=search, title='Add users')

    users = User.query.order_by(User.first_name).order_by(User.last_name)\
        .paginate(page_nr, 15, False)

    return render_template('group/add_users.htm', group=group, users=users,
                           title='Add users')


@blueprint.route('/groups/edit-permissions/<int:group_id>/',
                 methods=['GET', 'POST'])
@blueprint.route('/groups/edit-permissions/<int:group_id>/<int:page_nr>',
                 methods=['GET', 'POST'])
def edit_permissions(group_id, page_nr=1):
    if not(GroupPermissionAPI.can_read('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no group with id {}'.format(group_id), 'danger')
        return redirect(url_for('group.view'))

    permissions = GroupPermission.query.order_by(GroupPermission.module_name)\
        .filter(GroupPermission.group_id == group_id).all()

    form = EditGroupPermissionForm()

    # The application's blueprints are stored as a dict, with key
    # 'blueprint.name' and value '<Blueprint object>'.
    modules = application.blueprints.keys()

    # Remove current permission.
    for permission in permissions:
        try:
            modules.remove(permission.module_name)
        except ValueError:
            continue

    form.add_module_name.choices = [('', '')] + zip(modules, modules)

    if form.validate_on_submit():
        for form_entry, permission in zip(form.permissions, permissions):
            if permission.permission != form_entry.select.data:
                permission.permission = form_entry.select.data
                db.session.add(permission)
                db.session.commit()

        # If a permission is empty, remove it.
        permissions_cpy = copy.copy(permissions)
        for permission in permissions_cpy:
            if permission.permission == 0:
                permissions.remove(permission)
                db.session.delete(permission)

        db.session.commit()

        if form.add_module_name.data:
            new_permission = GroupPermission(form.add_module_name.data,
                                             group_id,
                                             form.add_module_permission.data)
            db.session.add(new_permission)
            db.session.commit()
            flash("Permission for module %s created!" %
                  (form.add_module_name.data))

        return redirect(url_for('group.edit_permissions', group_id=group_id,
                                page_nr=page_nr))
    else:
        flash_form_errors(form)

        # add the permissions as drop down boxes
        for permission in permissions:
            data = {}
            data['select'] = permission.permission
            form.permissions.append_entry(data)

    return render_template('group/edit_permissions.htm', form=form,
                           can_write=GroupPermissionAPI.can_write('group'),
                           group_name=group.name, title='Module permissions',
                           permissions=zip(permissions, form.permissions))


@blueprint.route('/api/group/users/<int:group_id>', methods=['GET'])
def group_api_get_users(group_id):
    group = Group.query.get(group_id)
    users = group.users.order_by(User.first_name, User.last_name).all()

    res = [{'val': user.id, 'label': user.name} for user in users]
    return jsonify(users=res)
