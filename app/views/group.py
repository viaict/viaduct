# coding: utf-8
import copy
import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import abort, jsonify
from flask_login import current_user

from app import app, db

from app.utils.module import ModuleAPI
from app.utils import google

from app.models.user import User
from app.models.group import Group
from app.models.permission import GroupPermission
from app.forms.group import EditGroupPermissionForm, ViewGroupForm, \
    CreateGroup, EditGroup

blueprint = Blueprint('group', __name__)


@blueprint.route('/groups/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:page_nr>/', methods=['GET', 'POST'])
def view(page_nr=1):
    if not(ModuleAPI.can_read('group')):
        return abort(403)

    form = ViewGroupForm(request.form)
    pagination = Group.query.order_by(Group.name).paginate(page_nr, 15, False)

    if form.validate_on_submit():
        if form.delete_group.data:
            if ModuleAPI.can_write('group'):
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

    return render_template('group/view.htm', form=form, pagination=pagination,
                           groups=zip(pagination.items, form.entries),
                           current_user=current_user, title='Groups')


@blueprint.route('/groups/create/', methods=['GET', 'POST'])
def create():
    if not(ModuleAPI.can_write('group')):
        return abort(403)

    form = CreateGroup(request.form)

    if form.validate_on_submit():
        name = request.form['name'].strip()
        maillist = request.form['maillist'].strip()
        committee_url = form.committee_url.data.strip()
        valid_form = True

        if Group.query.filter(Group.name == name).count() > 0:
            flash('The naam van de groep wordt al gebruikt', 'danger')
            valid_form = False

        if valid_form:
            maillist = maillist.strip().lower()
            if maillist == '':
                group = Group(name, None)
            else:
                group = Group(name, maillist)

            db.session.add(group)
            db.session.commit()

            flash('De groep is aangemaakt.', 'success')

            if committee_url != '':
                return redirect('%s?group_id=%d' % (
                    url_for('committee.edit_committee',
                            committee=committee_url), group.id))

            return redirect(url_for('group.view'))

    return render_template('group/create.htm', title='Maak groep',
                           form=form, group=None)


@blueprint.route('/groups/<int:group_id>/edit/', methods=['GET', 'POST'])
def edit(group_id):
    if not(ModuleAPI.can_write('group')):
        return abort(403)

    group = Group.by_id(group_id)

    form = EditGroup(request.form, group)
    if request.method == 'POST':
        form = EditGroup(request.form)

        if form.validate_on_submit():
            name = form.data['name'].strip()
            maillist = form.data['maillist'].strip().lower()

            suffix = maillist.find('@svia.nl')
            if suffix > 0:
                maillist = maillist[:suffix]

            valid_form = True

            group_with_same_name = Group.query.\
                filter(Group.name == name, Group.id != group_id).first()
            if group_with_same_name is not None:
                flash('The naam van de groep wordt al gebruikt', 'danger')
                valid_form = False

            if valid_form:
                group.name = name
                group.maillist = maillist
                if maillist == '':
                    group.maillist = None
                else:
                    group.maillist = maillist

                db.session.commit()
                google.create_group_if_not_exists(name, maillist)
                group.add_members_to_maillist()

                flash('De groep is aangepast.', 'success')

                return redirect(url_for('group.view'))

    return render_template('group/create.htm', title='Pas groep aan',
                           form=form, group=group)


@blueprint.route('/groups/<int:group_id>/users/', methods=['GET', 'POST'])
def view_users(group_id):
    if not(ModuleAPI.can_read('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no such group.')
        return redirect(url_for('group.view'))

    users = group.users.order_by(User.first_name)\
        .order_by(User.last_name).all()

    return render_template('group/view_users.htm', group=group, users=users,
                           title='%s users' % (group.name))


@blueprint.route('/groups/<int:group_id>/get_users/', methods=['GET'])
def get_group_users(group_id):
    if not(ModuleAPI.can_read('group')):
        return abort(403)
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
def delete_group_users(group_id):
    if not(ModuleAPI.can_write('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()
    if not group:
        flash('There is no such group.')
        return redirect(url_for('group.view'))

    user_ids = request.get_json()['selected_ids']

    users = group.get_users().filter(User.id.in_(user_ids))\
        .order_by(User.first_name).order_by(User.last_name).all()

    for user in users:
        group.delete_user(user)

        db.session.add(group)
        db.session.commit()

    return json.dumps({'status': 'success'})


@blueprint.route('/groups/<int:group_id>/users/add/', methods=['GET', 'POST'])
def add_users(group_id, page_nr=1):
    if not(ModuleAPI.can_write('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no such group.', 'danger')
        return redirect(url_for('group.view'))

    return render_template('group/add_users.htm',
                           group=group, title='Add users')


@blueprint.route('/groups/edit-permissions/<int:group_id>/',
                 methods=['GET', 'POST'])
@blueprint.route('/groups/edit-permissions/<int:group_id>/<int:page_nr>/',
                 methods=['GET', 'POST'])
def edit_permissions(group_id, page_nr=1):
    if not(ModuleAPI.can_read('group')):
        return abort(403)

    group = Group.query.filter(Group.id == group_id).first()

    if not group:
        flash('There is no group with id {}'.format(group_id), 'danger')
        return redirect(url_for('group.view'))

    permissions = GroupPermission.query.order_by(GroupPermission.module_name)\
        .filter(GroupPermission.group_id == group_id).all()

    form = EditGroupPermissionForm()

    # The app's blueprints are stored as a dict, with key
    # 'blueprint.name' and value '<Blueprint object>'.
    modules = list(app.blueprints.keys())

    # Remove current permission.
    for permission in permissions:
        try:
            modules.remove(permission.module_name)
        except ValueError:
            continue

    form.add_module_name.choices = [('', '')] + list(zip(modules, modules))

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

    # add the permissions as drop down boxes
    for permission in permissions:
        data = {}
        data['select'] = permission.permission
        form.permissions.append_entry(data)

    return render_template('group/edit_permissions.htm', form=form,
                           can_write=ModuleAPI.can_write('group'),
                           group_name=group.name, title='Module permissions',
                           permissions=zip(permissions, form.permissions))


@blueprint.route('/api/group/users/<int:group_id>/', methods=['GET'])
def group_api_get_users(group_id):
    if not(ModuleAPI.can_read('group')):
        return abort(403)
    group = Group.query.get(group_id)
    users = group.users.order_by(User.first_name, User.last_name).all()

    res = [{'val': user.id, 'label': user.name} for user in users]
    return jsonify(users=res)


@blueprint.route('/groups/<int:group_id>/users/add_users/', methods=['PUT'])
def group_api_add_users(group_id):
    if not(ModuleAPI.can_write('group')):
        return abort(403)
    group = Group.query.get(group_id)

    user_ids = request.get_json()['selected_ids']
    add_users = User.query.filter(User.id.in_(user_ids)).all()

    for user in add_users:
        group.add_user(user)

    db.session.add(group)
    db.session.commit()
    return "testestetsetset", 200
