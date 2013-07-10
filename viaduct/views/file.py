'''
Views for the file module.
'''
from flask import Blueprint, render_template, request, flash, redirect, url_for
from viaduct.models.file import File
from viaduct.forms import FileForm
from viaduct.api import FileAPI

blueprint = Blueprint('file', __name__)

@blueprint.route('/files/', methods=['GET'])
@blueprint.route('/files/<int:page>/', methods=['GET'])
def list(page=1):
	'''
	List all files that are not assigned to a page.
	'''
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
	new_file = request.files['file']
	FileAPI.upload(new_file)

	return redirect(url_for('file.list', page=page))
