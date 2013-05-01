import os
from flask import Blueprint
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from sqlalchemy import or_

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from models import Examination
from viaduct.models import Course, Education

from werkzeug import secure_filename

blueprint = Blueprint('examination', __name__)

UPLOAD_FOLDER = '/home/bram/via_ict/viaduct/viaduct/static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@blueprint.route('/examination/add', methods=['GET', 'POST'])
def upload_file():
	courses =  Course.query.all()
	educations =  Education.query.all()

	if request.method == 'POST':
		file = request.files['file']
		title = request.form.get("title", None)
		course = request.form.get("course", None)
		education = request.form.get("education", None)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
			exam = Examination(filename, title,  course, education)
			db.session.add(exam)
			db.session.commit()

			return render_template('examination/upload.htm', courses = courses, 
			educations = educations, message = 'Het tentamen is geupload!');

	return render_template('examination/upload.htm', courses = courses, 
		educations = educations);


@blueprint.route('/examination/', methods=['GET', 'POST'])
def view_examination():
	path = '../static/'

	if request.method == 'POST':
		search = request.form.get("search", None)
		examinations =  Examination.query.\
			filter(Examination.title.like('%' + search + '%')).all()
		return render_template('examination/view.htm', path = path, 
			examinations = examinations)


	examinations = Examination.query.all()
	print examinations
	return render_template('examination/view.htm', path = path, 
		examinations = examinations)

@blueprint.route('/course/add', methods=['GET', 'POST'])
def add_course():
	if request.method == 'POST':
		course = request.form.get("course", None)
		discription = request.form.get("discription", None)
		new_course = Course(course, discription)
		db.session.add(new_course)
		db.session.commit()
		return redirect('../examination/add')

	return render_template('examination/course.htm')

@blueprint.route('/education/add', methods=['GET', 'POST'])
def add_education():
	if request.method == 'POST':
		education = request.form.get("education", None)
		new_education = Education(1, education)
		db.session.add(new_education)
		db.session.commit()
		return redirect('../examination/add')

	return render_template('examination/education.htm')


