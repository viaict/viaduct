import os

from flask import Blueprint
from flask import abort, flash, session, redirect, render_template, request,\
    url_for
from flask.ext.login import login_required, current_user

from viaduct import application, db
from viaduct.api import GroupPermissionAPI
from viaduct.models import ExaminationRevision, Course, Education, Page
from viaduct.forms import ExaminationForm
from viaduct.helpers import flash_form_errors

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
    while file_exists(temp_filename):
        split = filename.split('.')
        split[0] = split[0] + "(" + str(i) + ")"
        temp_filename = split[0] + "." + split[len(split)-1]
        i += 1
    return temp_filename


@blueprint.route('/examination/', methods=['GET'])
@blueprint.route('/examination/page/<int:page_nr>/', methods=['GET'])
@login_required
def list(page_nr=1):
    if not GroupPermissionAPI.can_read('examination'):
        return abort(403)

    path = '/static/uploads/examinations/'

    exasub = db.session.query(db.func.max(ExaminationRevision.id)
                                   .label('max_id'))\
        .group_by(ExaminationRevision.instance_id).subquery()

    exas = ExaminationRevision.query\
        .join(exasub, ExaminationRevision.id == exasub.c.max_id)\
        .join(Course)

    if request.args.get('search'):
        search = request.args.get('search')

        exas = exas.join(Education)\
            .filter(db.or_(ExaminationRevision.title.like('%' + search + '%'),
                           Course.name.like('%' + search + '%'),
                           Education.name.like('%' + search + '%')))
    else:
        search = ''

    exas = exas.order_by(Course.name).paginate(page_nr, 15, True)

    return render_template('examination/list.htm', path=path,
                           examinations=exas, search=search)


@blueprint.route('/create/examination/', methods=['GET', 'POST'])
@blueprint.route('/edit/examination/<int:instance_id>/',
                 methods=['GET', 'POST'])
def edit(instance_id=None):
    if not GroupPermissionAPI.can_write('examination'):
        return abort(403)

    data = request.form

    if instance_id:
        revision = ExaminationRevision.get_latest(instance_id)

        if not revision:
            return abort(404)

        page = revision.page

        form = ExaminationForm(data, revision)
    else:
        instance_id = ExaminationRevision.get_new_id()
        form = ExaminationForm()
        page = None

    form.course_id.choices = [(c.id, c.name) for c in Course.query.all()]
    form.education_id.choices = [(e.id, e.name) for e in Education.query.all()]

    path = request.files[form.path.name]
    print(path)
    if form.validate_on_submit():
        path = request.files[form.path.name]
        print(path)
        answer_path = request.files[form.answer_path.name]
        title = data['title'].strip()
        comment = data['comment'].strip()
        course_id = data.get('course_id', None)
        education_id = data.get('education_id', None)


        error = False

        real_path = upload_file_real(path)
        if not real_path:
            flash('Fout formaat tentamen', 'danger')
            error = True

        real_answer_path = upload_file_real(answer_path)
        if not real_answer_path:
            flash('Fout formaat antwoorden', 'danger')
            error = True

        if error:
            return render_template('examination/edit.htm', page=page,
                                   form=form)

        if not page:
            page = Page('examination/%d/' % (instance_id), 'examination')
            page.needs_payed = False

            db.session.add(page)
            db.session.commit()

        new_revision = ExaminationRevision(page, title, comment, instance_id,
                                           real_path, real_answer_path,
                                           current_user.id, course_id,
                                           education_id)

        db.session.add(new_revision)
        db.session.commit()

        flash('Het tentamen is geupload', 'success')

        return redirect(url_for('page.get_page', path=page.path))

    else:
        flash_form_errors(form)

    form.comment.data = ''

    return render_template('examination/edit.htm', page=page, form=form)


@blueprint.route('/examination/admin', methods=['GET', 'POST'])
@blueprint.route('/examination/admin/<int:page_nr>/', methods=['GET', 'POST'])
def examination_admin(page_nr=1):
    if not GroupPermissionAPI.can_write('examination', False):
        session['prev'] = 'examination.examination_admin'
        return abort(403)

    path = '/static/uploads/examinations/'

    if request.args.get('search'):
        search = request.args.get('search')
        examinations = ExaminationRevision.query.join(Course).join(Education)\
            .filter(db.or_(ExaminationRevision.title.like('%' + search + '%'),
                           Course.name.like('%' + search + '%'),
                           Education.name.like('%' + search + '%')))\
            .paginate(page_nr, 15, False)
        return render_template('examination/admin.htm', path=path,
                               examinations=examinations, search=search,
                               message="")

    if request.args.get('delete'):
        exam_id = request.args.get('delete')
        examination = ExaminationRevision.query.filter(ExaminationRevision.id == exam_id)\
            .first()

        os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
        title = examination.title
        db.session.delete(examination)
        db.session.commit()
        examinations = ExaminationRevision.query.paginate(page_nr, 15, False)
        return render_template('examination/admin.htm', path=path,
                               examinations=examinations, search="",
                               message="Tentamen " + title +
                                       " succesvol verwijderd")

    if request.args.get('edit'):
        exam_id = request.args.get('edit')
        examination = ExaminationRevision.query.filter(ExaminationRevision.id == exam_id)\
            .first()

        os.remove(os.path.join(UPLOAD_FOLDER, examination.path))
        db.session.delete(examination)
        db.session.commit()

    examinations = ExaminationRevision.query.paginate(page_nr, 15, False)
    return render_template('examination/admin.htm', path=path,
                           examinations=examinations, search="", message="")


@blueprint.route('/examination/edit', methods=['GET', 'POST'])
@login_required
def edit_examination():
    if not GroupPermissionAPI.can_write('examination', True):
        session['prev'] = 'examination.edit_examination'
        return abort(403)

    path = '../static/'

    courses = Course.query.all()
    educations = Education.query.all()
    message = False

    if request.method == 'POST':
        file = request.files['file']
        answers = request.files['answers']
        title = request.form.get("title", None)
        course_id = request.form.get("course", None)
        education_id = request.form.get("education", None)
        exam_id = request.form.get("examination", None)

        if not title:
            flash('Geen titel opgegeven', 'error')
            print("wut")

        if title and education_id and exam_id:
            examination = ExaminationRevision.query.filter(ExaminationRevision.id == exam_id)\
                .first()

            examination.title = title
            examination.course_id = course_id
            examination.education_id = education_id

            if not title:
                flash('Geen titel opgegeven', 'error')

            if file.name:
                examination.path = upload_file_real(file, examination.path)
                if not examination.path:
                    flash('Fout formaat tentamen', 'error')
            else:
                flash('Geen tentamen opgegeven', 'error')

            if answers:
                examination.answer_path = upload_file_real(answers)
                if not examination.answer_path:
                    flash('Fout formaat antwoorden', 'error')
                if examination.answer_path:
                    examination.answer_path = None

            if message:
                return render_template('examination/edit.htm', courses=courses,
                                       educations=educations,
                                       examination=examination, message='')

            # if file:
            #   if allowed_file(file.filename):
            #       filename = secure_filename(file.filename)
            #       filename = create_unique_file(filename)

            #       os.remove(os.path.join(UPLOAD_FOLDER,
            #               examination.path))

            #       file.save(os.path.join(UPLOAD_FOLDER, filename))

            #       examination.path = filename
            #   else:
            #       return render_template('examination/edit.htm',
            #                              courses = courses,
            #       educations = educations, examination=examination,
            #       message = 'Fout file format!');

            db.session.commit()

            flash('Het tentamen is aangepast!')
            return render_template('examination/edit.htm', courses=courses,
                                   educations=educations,
                                   examination=examination,
                                   message='Het tentamen is aangepast!')

    if request.args.get('edit'):
        exam_id = request.args.get('edit')
        examination = ExaminationRevision.query.filter(ExaminationRevision.id == exam_id)\
            .first()

        return render_template('examination/edit.htm', path=path,
                               examination=examination, courses=courses,
                               educations=educations)

    examinations = ExaminationRevision.query.all()
    return render_template('examination/admin.htm', path=path,
                           examinations=examinations, search="",
                           message="Geen examen geselecteerd")


@blueprint.route('/course/add', methods=['GET', 'POST'])
def add_course():
    if not GroupPermissionAPI.can_write('examination'):
        session['prev'] = 'examination.add_course'
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
        session['prev'] = 'examination.add_education'
        return abort(403)

    if request.method == 'POST':
        education = request.form.get("education", None)
        new_education = Education(1, education)

        db.session.add(new_education)
        db.session.commit()
        return redirect('../examination/add')

    return render_template('examination/education.htm')


def get_education_id(education):
    education_object = db.session.query(Education)\
        .filter(Education.name == education).first()

    if not education_object:
        return None
    return education_object[0].id


def get_course_id(course):
    course_object = db.session.query(Course).filter(Course.name == course)\
        .first()

    if not course_object:
        return None
    return course_object.id


def upload_file_real(file, old_path='1'):
    if file:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = create_unique_file(filename)

            if old_path != '1':
                os.remove(os.path.join(UPLOAD_FOLDER, old_path))

            file.save(os.path.join(UPLOAD_FOLDER, filename))

            return filename
        else:
            return False
    else:
        return True
