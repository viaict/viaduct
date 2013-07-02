from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import abort
from flask.ext.login import current_user

from viaduct import db
from viaduct.helpers import flash_form_errors

from viaduct.models import user_group, Group, GroupPermission, User, UserPermission, Permission
from viaduct.forms.group import EditGroupPermissionForm, ViewGroupForm

blueprint = Blueprint('group', __name__)

@blueprint.route('/groups/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:page_id>/', methods=['GET', 'POST'])
def view(page_id=1):
	if not current_user.has_permission('group.view'):
		abort(403)

	form = ViewGroupForm(request.form)
	pagination = Group.query.paginate(page_id, 15, False)

	if form.validate_on_submit():
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
		for group in pagination.items:
			form.entries.append_entry()

		flash_form_errors(form)

	return render_template('group/view.htm', form=form, pagination=pagination,
			groups=zip(pagination.items, form.entries))

@blueprint.route('/groups/create/', methods=['GET', 'POST'])
def create():
	if not current_user.has_permission('group.create'):
		abort(403)

	if request.method == 'POST':
		name = request.form['name'].strip()
		valid_form = True

		if not name:
			flash('No group name has been specified.', 'error')
			valid_form = False
		elif Group.query.filter(Group.name==name).count() > 0:
			flash('The group name that has been specified is in use already.', 'error')
			valid_form = False

		if valid_form:
			group = Group(name)

			db.session.add(group)
			db.session.commit()

			flash('The group has been created.', 'success')

			return redirect(url_for('group.view'))

	return render_template('group/create.htm')

@blueprint.route('/groups/<int:group_id>/users/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:group_id>/users/<int:page_id>/', methods=['GET', 'POST'])
def view_users(group_id, page_id=1):
	if not current_user.has_permission('group.view'):
		abort(403)

	group = Group.query.filter(Group.id==group_id).first()

	if not group:
		flash('There is no such group.')

		return redirect(url_for('group.view'))

	if request.method == 'POST':
		user_ids = request.form.getlist('select')

		users = group.get_users().filter(User.id.in_(user_ids)).all()

		for user in users:
			group.delete_user(user)

		db.session.add(group)
		db.session.commit()

		if len(user_ids) > 1:
			flash('The selected users have been deleted.', 'success')
		else:
			flash('The selected user has been deleted.', 'success')

		return redirect(url_for('group.view_users', group_id=group_id))

	users = group.get_users().paginate(page_id, 15, False)

	return render_template('group/view_users.htm', group=group, users=users)

@blueprint.route('/groups/<int:group_id>/users/add/', methods=['GET', 'POST'])
@blueprint.route('/groups/<int:group_id>/users/add/<int:page_id>', methods=['GET', 'POST'])
def add_users(group_id, page_id=1):
	if not current_user.has_permission('group.add_users'):
		abort(403)

	group = Group.query.filter(Group.id==group_id).first()

	if not group:
		flash('There is no such group.')

		return redirect(url_for('group.view'))

	if request.method == 'POST':
		user_ids = request.form.getlist('select')

		users = User.query.filter(User.id.in_(user_ids)).all()

		for user in users:
			group.add_user(user)

		db.session.add(group)
		db.session.commit()

		if len(user_ids) > 1:
			flash('The selected users have been added to the group.', 'success')
		else:
			flash('The selected user has been added to the group.', 'success')

		return redirect(url_for('group.view_users', group_id=group_id))

	users = User.query.paginate(page_id, 15, False)

	return render_template('group/add_users.htm', group=group, users=users)

@blueprint.route('/groups/edit-permissions/<int:group_id>/', methods=['GET', 'POST'])
@blueprint.route('/groups/edit-permissions/<int:group_id>/<int:page_id>', methods=['GET', 'POST'])
def edit_permissions(group_id, page_id=1):
	if not current_user.has_permission('group.edit'):
		abort(403)

	group = Group.query.filter(Group.id==group_id).first()
	form = EditGroupPermissionForm()
	pagination = Permission.query.paginate(page_id, 15, False)

	if form.validate_on_submit():
		for form_entry, permission in zip(form.permissions, pagination.items):
			if form_entry.select.data > 0:
				group.add_permission(permission.name, True)
			else:
				group.delete_permission(permission.name)

		return redirect(url_for('group.view'))
	else:
		for permission in pagination.items:
			data = {}

			if group.get_permission(permission.name) > 0:
				data['select'] = 1
			else:
				data['select'] = -1

			form.permissions.append_entry(data)

	return render_template('group/edit_permissions.htm', form=form,
			pagination=pagination,
			permissions=zip(pagination.items, form.permissions))

