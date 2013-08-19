from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors
from viaduct.models.group import Group


from viaduct.api.module_permission import ModulePermissionAPI
from viaduct.forms.module_permission import ModuleEditGroupPermissionForm
from viaduct.models.module_permission import ModulePermission

blueprint = Blueprint('module_permission', __name__);

@blueprint.route("/module_permission/<int:group_id>", methods=['GET', 'POST'])
def main_view(group_id):
	if not(ModulePermissionAPI.can_read('module_permission')):
		return abort(403);

	group = Group.query.filter(Group.id==group_id).first()
	# TODO: change into error if group_name is unknown
	group_name = "unknown" if group == None else group.name

	permissions = ModulePermission.query.filter(ModulePermission.group_id==group_id).all()

	form = ModuleEditGroupPermissionForm()


	make_form = False
	if form.validate_on_submit():
		make_form = True

		for form_entry, permission in zip(form.permissions, permissions):
			if permission.permission != form_entry.select.data:
				permission.permission = form_entry.select.data
				db.session.add(permission)
				db.session.commit()

	else:
		flash_form_errors(form)

		# add the permissions as drop down boxes
		for permission in permissions:
			data = {}
			data['select'] = permission.permission
			form.permissions.append_entry(data)


	return render_template('module_permission/view.htm', form=form,
		can_write=ModulePermissionAPI.can_write('module_permission'),
		group_name=group_name, permissions=zip(permissions, form.permissions))





