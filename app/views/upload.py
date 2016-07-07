import os

from flask import abort, Blueprint, redirect, request, render_template, \
    send_file, url_for
from flask_login import current_user
from werkzeug import secure_filename

from app import app
from app.forms import UploadForm
from app.utils.forms import flash_form_errors
from app.utils.module import ModuleAPI

blueprint = Blueprint('upload', __name__)


@blueprint.route('/file/')
@blueprint.route('/file/<filename>/')
def view(filename=''):
    return ''


@blueprint.route('/file/direct/<filename>')
def view_direct(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    path = os.path.join(app.root_path, file_path)

    if not os.path.exists(path):
        abort(404)

    return send_file(file_path, as_attachment=True)


@blueprint.route('/file/add/', methods=['GET', 'POST'])
def add():
    if not ModuleAPI.can_write('file') or current_user.is_anonymous:
        return abort(403)

    form = UploadForm(request.form)

    if form.validate_on_submit():
        file = request.files['upload']

        if file:
            filename = form.filename.data
            original = secure_filename(file.filename)

            if len(os.path.splitext(filename)[1]) == 0:
                filename += os.path.splitext(original)[1]

            file_path = os.path.join(app.root_path,
                                     app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(file_path, filename)

            file.save(file_path)

            return redirect(url_for('file.view', filename=filename))
    else:
        flash_form_errors(form)

    return render_template('upload/add_file.htm', form=form,
                           title='Upload files')
