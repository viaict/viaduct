"""Views for the file module."""
from flask import Blueprint, render_template, request, flash

from app.decorators import require_role
from app.forms.file import FileForm
from app.models.file import File
from app.roles import Roles
from app.utils.file import file_upload, file_search

blueprint = Blueprint('file', __name__, url_prefix='/files')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/<int:page_nr>/', methods=['GET'])
@require_role(Roles.FILE_READ)
def list(page_nr=1):
    """List all files that are not assigned to a page."""
    if request.args.get('search'):
        search = request.args.get('search', None)
        filters = file_search(search)
        files = File.query.filter(File.name.in_(filters),
                                  File.page == None)  # noqa
    else:
        files = File.query.filter(File.page == None)  # noqa

    files = files.order_by(File.name).paginate(page_nr, 30, False)

    form = FileForm()

    return render_template('files/list.htm', files=files, form=form)


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

    files = File.query.filter_by(page=None).order_by(File.name)\
        .paginate(page_nr, 30, False)
    form = FileForm()

    hostname = request.headers.get('Origin', '')

    return render_template('files/list.htm', **locals())
