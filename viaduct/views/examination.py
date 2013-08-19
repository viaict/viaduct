import os
from flask import Blueprint
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask.ext.login import current_user

from sqlalchemy import or_

from viaduct import application, db
from viaduct.helpers import flash_form_errors

from viaduct.models.examination import Examination
from viaduct.models.course import Course
from viaduct.models.education import Education

from viaduct.api.group import GroupPermissionAPI

from werkzeug import secure_filename

blueprint = Blueprint('examination', __name__)

UPLOAD_FOLDER = application.config['EXAMINATION_UPLOAD_FOLDER']
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def file_exists(filename):
	return os.path.exists(os.path.join(UPLOAD_FOLDER, filename))

def create_unique_file(filename):
	temp_filename = filename

	i = 0
	while(file_exists(temp_filename) == True):
		split = filename.split('.')
		split[0] = split[0] + "(" + str(i) + ")";
		temp_filename = split[0] + "." + split[len(split)-1]
		i += 1
	return temp_filename



@blueprint.route('/examination/add', methods=['GET', 'POST'])
def upload_file():
	if not GroupPermissionAPI.can_write('examination'):
		return abort(403)

	courses = Course.query.all()
	educations = Education.query.all()

	if request.method == 'POST':
		file = request.files['file']
		title = request.form.get("title", None)
		course_id = request.form.get("course", None)
		education_id = request.form.get("education", None)

		# course_id = get_course_id(course);
		# if(course_id == None):
		# 	return render_template('examination/upload.htm', courses = courses,
		# 	educations = educations, message = 'Er is een fout opgetreden!');
		# education_id = get_education_id(education)
		# if(education_id == None):
		# 	return render_template('examination/upload.htm', courses = courses,
		# 	educations = educations, message = 'Er is een fout opgetreden!');

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filename = create_unique_file(filename)

			file.save(os.path.join(UPLOAD_FOLDER, filename))
			exam = Examination(filename, title, course_id, education_id)
			db.session.add(exam)
			db.session.commit()

			return render_template('examination/upload.htm', courses = courses,
			educations = educations, message = 'Het tentamen is geupload!');
		else:
			return render_template('examination/upload.htm', courses = courses,
			educations = educations, message = 'Fout file format!');

	return render_template('examination/upload.htm', courses = courses,
		educations = educations);


@blueprint.route('/examination/', methods=['GET', 'POST'])
@blueprint.route('/tentamenbank/', methods=['GET', 'POST'])
def view_examination():
	path = '/static/uploads/examinations/'

	if request.args.get('search') != None:
		search = request.args.get('search')
		examinations = Examination.query.join(Course).join(Education).\
			filter(or_(Examination.title.like('%' + search + '%'),
				Course.name.like('%' + search + '%'),
				Education.name.like('%' + search + '%'))).all()
		return render_template('examination/view.htm', path = path,
			examinations = examinations, search=search)


	examinations = Examination.query.all()
	return render_template('examination/view.htm', path = path,
		examinations = examinations, search="")

@blueprint.route('/examination/admin', methods=['GET', 'POST'])
def examination_admin():
	if not GroupPermissionAPI.can_write('examination'):
		return abort(403)

	path = '/static/uploads/examinations/'

	if request.args.get('search') != None:
		search = request.args.get('search')
		examinations = Examination.query.join(Course).join(Education).\
			filter(or_(Examination.title.like('%' + search + '%'),
				Course.name.like('%' + search + '%'),
				Education.name.like('%' + search + '%'))).all()
		return render_template('examination/admin.htm', path = path,
			examinations = examinations, search=search, message="")

	if request.args.get('delete') != None:
		exam_id = request.args.get('delete')
		examination = Examination.query.filter(Examination.id == exam_id).first()

		os.remove(os.path.join(UPLOAD_FOLDER,
		examination.path))
		title = examination.title
		db.session.delete(examination)
		db.session.commit()
		examinations = Examination.query.all()
		return render_template('examination/admin.htm', path = path,
			examinations = examinations, search="",
			message="Tentamen " + title + " succesvol verwijderd")

	if request.args.get('edit') != None:
		exam_id = request.args.get('edit')
		examination = Examination.query.filter(Examination.id == exam_id).first()

		os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
		db.session.delete(examination)
		db.session.commit()

	examinations = Examination.query.all()
	return render_template('examination/admin.htm', path = path,
		examinations = examinations, search="", message="")

@blueprint.route('/examination/edit', methods=['GET', 'POST'])
def edit_examination():
	if not GroupPermissionAPI.can_write('examination'):
		return abort(403)

	path = '../static/'

	courses = Course.query.all()
	educations = Education.query.all()

	if request.method == 'POST':
		file = request.files['file']
		title = request.form.get("title", None)
		course_id = request.form.get("course", None)
		education_id = request.form.get("education", None)
		exam_id = request.form.get("examination", None)

		if title and education_id and exam_id:
			examination = Examination.query.filter(Examination.id == exam_id).\
				first()

			examination.title = title
			examination.course_id = course_id
			examination.education_id = education_id

			if file:
				if allowed_file(file.filename):
					filename = secure_filename(file.filename)
					filename = create_unique_file(filename)

					os.remove(os.path.join(UPLOAD_FOLDER,
							examination.path))

					file.save(os.path.join(UPLOAD_FOLDER, filename))

					examination.path = filename
				else:
					return render_template('examination/edit.htm', courses = courses,
					educations = educations, examination=examination,
					message = 'Fout file format!');

			db.session.commit()

			return render_template('examination/edit.htm', courses = courses,
			educations = educations, examination=examination,
			message = 'Het tentamen is aangepast!');

	if request.args.get('edit') != None:
		exam_id = request.args.get('edit')
		examination = Examination.query.filter(Examination.id == exam_id).\
			first()

		return render_template('examination/edit.htm', path = path,
			examination=examination, courses=courses, educations=educations)



	examinations = Examination.query.all()
	return render_template('examination/admin.htm', path = path,
		examinations = examinations, search="",
		message="Geen examen geselecteerd")

@blueprint.route('/course/add', methods=['GET', 'POST'])
def add_course():
	if not GroupPermissionAPI.can_write('examination'):
		return abort(403)

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
	if not GroupPermissionAPI.can_write('examination'):
		return abort(403)

	if request.method == 'POST':
		education = request.form.get("education", None)
		new_education = Education(1, education)

		db.session.add(new_education)
		db.session.commit()
		return redirect('../examination/add')

	return render_template('examination/education.htm')


def get_education_id(education):
	education_object = db.session.query(Education).\
		filter(Education.name==education).first()

	if(education_object == None):
		return None
	return education_object[0].id

def get_course_id(course):
	course_object = db.session.query(Course).filter(Course.name==course).first()

	if(course_object == None):
		return None
	return course_object.id
