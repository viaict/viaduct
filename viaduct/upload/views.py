from flask import send_from_directory

from viaduct import application

@module.route('/uploads/<filename>')
def get_upload(filename):
	return send_from_directory(application.config['UPLOAD_FOLDER'], filename)

