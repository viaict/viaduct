"""Views for the file module."""
from flask import Blueprint, render_template, request, flash, abort
from flask_login import current_user

from app.decorators import require_role
from app.forms.file import FileForm
from app.models.file import File
from app.enums import FileCategory
from app.roles import Roles
from app.service import role_service
from app.utils.file import file_upload, file_search
from app.service import file_service

blueprint = Blueprint('file', __name__, url_prefix='/files')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/<int:page_nr>/', methods=['GET'])
@require_role(Roles.FILE_READ)
def list(page_nr=1):
    """List all files that are not assigned to a page."""
    if request.args.get('search'):
        search = request.args.get('search', None)
        filters = file_search(search)
        files = File.query.filter(File.display_name.in_(filters))
    else:
        files = File.query

    files = files.order_by(File.display_name).paginate(page_nr, 30, False)

    form = FileForm()

    can_write = role_service.user_has_role(current_user, Roles.FILE_WRITE)

    return render_template('files/list.htm', files=files, form=form,
                           can_write=can_write)


@blueprint.route('/', methods=['POST'])
@blueprint.route('/<int:page_nr>/', methods=['POST'])
@require_role(Roles.FILE_WRITE)
def upload(page_nr=1):
    """Upload a file."""
    new_files = []
    for new_file_name in request.files.getlist('file'):
        # File upload request, but no added files
        if new_file_name.filename == '':
            flash("No files selected", 'danger')
            return list(page_nr=page_nr)
        file = file_upload(new_file_name)
        if file:
            new_files.append(file)

    files = File.query.filter_by(page=None).order_by(File.display_name)\
        .paginate(page_nr, 30, False)
    form = FileForm()

    hostname = request.headers.get('Origin', '')
    can_write = role_service.user_has_role(current_user, Roles.FILE_WRITE)

    return render_template('files/list.htm', **locals())


@blueprint.route('/content/<int:file_id>/<string:file_hash>/', methods=['GET'])
def file_content(file_id, file_hash):
    f = file_service.get_file_by_id(file_id)

    if f.hash != file_hash:
        return abort(404)

    if (f.category == FileCategory.EXAMINATION or
            f.category == FileCategory.ALV_DOCUMENT) and \
            (current_user.is_anonymous or not current_user.has_paid):
        return abort(404)

    mimetype = file_service.get_file_mimetype(f)
    content = file_service.get_file_content(f)

    if mimetype is None:
        mimetype = 'application/octet-stream'

    headers = {'Content-Type': mimetype}

    if f.display_name is not None:
        fn = f.display_name
        if len(f.extension) > 0:
            fn += "." + f.extension
        headers['Content-Disposition'] = 'inline; filename="{}"'.format(fn)

    return content, headers
