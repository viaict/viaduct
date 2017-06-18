"""Views for the file module."""
from flask import Blueprint, render_template, request, abort
from app.models.file import File
from app.forms import FileForm
from app.utils.file import file_upload, file_search
from app.utils.module import ModuleAPI

blueprint = Blueprint('file', __name__, url_prefix='/files')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/<int:page_nr>/', methods=['GET'])
def list(page_nr=1):
    """List all files that are not assigned to a page."""
    if not ModuleAPI.can_read('file'):
        return abort(403)

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
def upload(page_nr=1):
    """Upload a file."""
    if not ModuleAPI.can_write('file'):
        return abort(403)

    new_files = []
    for new_file_name in request.files.getlist('file'):
        new_files.append(file_upload(new_file_name))

    # File upload request, but no added files
    if new_files[0] is None:
        return list(page_nr=page_nr)

    files = File.query.filter_by(page=None).order_by(File.name)\
        .paginate(page_nr, 30, False)
    form = FileForm()

    hostname = request.headers.get('Origin', '')

    return render_template('files/list.htm', **locals())
