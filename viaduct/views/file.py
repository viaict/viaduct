'''
Views for the file module.
'''
from flask import Blueprint, render_template, request, flash, redirect, \
		url_for, jsonify, abort
from viaduct.models.file import File
from viaduct.forms import FileForm
from viaduct.api import FileAPI
from viaduct.api.group import GroupPermissionAPI

blueprint = Blueprint('file', __name__)

@blueprint.route('/files/', methods=['GET'])
@blueprint.route('/files/<int:page>/', methods=['GET'])
def list(page=1):
	'''
	List all files that are not assigned to a page.
	'''
	if not GroupPermissionAPI.can_read('file'):
		return abort(403)

	files = File.query.filter_by(page=None).order_by(File.name)\
			.paginate(page, 30, False)
	form = FileForm()

	return render_template('files/list.htm', files=files, form=form)

@blueprint.route('/files/', methods=['POST'])
@blueprint.route('/files/<int:page>/', methods=['POST'])
def upload(page=1):
	'''
	Upload a file.
	'''
	if not GroupPermissionAPI.can_write('file'):
		return abort(403)

	new_file = request.files['file']
	FileAPI.upload(new_file)

	return redirect(url_for('file.list', page=page))

@blueprint.route('/files/search/<string:query>/', methods=['GET'])
def search(query):
	'''
	Fuzzy search files.
	'''
	if not GroupPermissionAPI.can_read('file'):
		return jsonify(error='Geen toestemming');

	return jsonify(filenames=FileAPI.search(query))
