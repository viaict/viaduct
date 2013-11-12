from flask import Blueprint, abort, redirect, url_for
from flask import flash, render_template, request, jsonify
from flask.ext.login import current_user

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from viaduct.models.examination import Examination
from viaduct.models.course import Course
from viaduct.models.education import Education

from viaduct.api.search import SearchAPI


#### THIS IS A TEST MODULE, currently testing the searchAPI

#from viaduct.models.group import Group

#from viaduct.api.module_permission import ModulePermissionAPI
#from viaduct.forms.module_permission import ModuleEditGroupPermissionForm
#from viaduct.models.module_permission import ModulePermission

blueprint = Blueprint('module_permission', __name__, url_prefix='/module_permission')

@blueprint.route('/', methods=['GET', 'POST'])
def main_view():
	stack = [ (Examination, [Examination.title]),
			(Course, [Course.name]),
			(Education, [Education.name])]
	#stack = [ (Education, [Education.name]) ]
	needle = "inf ku"
	result = SearchAPI.search(stack, needle)
	print 'result from module_permission view: ', result
	return render_template('module_permission/view.htm', result=result)
	#	if not(ModulePermissionAPI.can_read('module_permission')):
	#		return abort(403);
	#
	#	group = Group.query.filter(Group.id==group_id).first()
	#	# TODO: change into error if group_name is unknown
	#	group_name = "unknown" if group == None else group.name
	#
	#	permissions = ModulePermission.query.filter(ModulePermission.group_id==group_id).all()
	#
	#	form = ModuleEditGroupPermissionForm()
	#
	#	make_form = False #	if form.validate_on_submit():
	#		make_form = True
	#
	#		for form_entry, permission in zip(form.permissions, permissions):
	#			if permission.permission != form_entry.select.data:
	#				permission.permission = form_entry.select.data
	#				db.session.add(permission)
	#				db.session.commit()
	#
	#	else:
	#		flash_form_errors(form)
	#
	#		# add the permissions as drop down boxes
	#		for permission in permissions:
	#			data = {}
	#			data['select'] = permission.permission
	#			form.permissions.append_entry(data)
	#
	#
	#	return render_template('module_permission/view.htm', form=form,
	#can_write=ModulePermissionAPI.can_write('module_permission'),
	#group_name=group_name, permissions=zip(permissions, form.permissions))





