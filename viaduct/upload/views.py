from flask import Blueprint
from flask import send_from_directory

from viaduct import application

from api import UploadAPI

module = Blueprint('upload', __name__)

#@module.route('/uploads/<filename>')
#def get_file(filename):
#	return send_from_directory(application.config['UPLOAD_FOLDER'], filename)

@module.route('/uploads/add', methods=['GET', 'POST'])
def add_file():
	return UploadAPI.add_file()

