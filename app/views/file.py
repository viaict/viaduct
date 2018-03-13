"""Views for the file module."""
from fuzzywuzzy import fuzz

from flask import Blueprint, render_template, request, flash, \
    abort, redirect, url_for
from flask_login import current_user

from app.decorators import require_role
from app.forms.file import FileForm
from app.enums import FileCategory
from app.roles import Roles
from app.service import role_service, file_service

blueprint = Blueprint('file', __name__, url_prefix='/files')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/<int:page_nr>/', methods=['GET'])
@require_role(Roles.FILE_READ)
def list(page_nr=1):
    """List all files that are not assigned to a page."""

    search = request.args.get('search', None)
    per_page = 30

    if search:
        search = search.lower()
        all_files = file_service.get_all_files_in_category(
            FileCategory.UPLOADS)
        file_scores = {}

        for f in all_files:
            score = fuzz.partial_ratio(search, f.full_display_name)
            if score > 75:
                file_scores[f] = score

        files = sorted(file_scores,
                       key=file_scores.get, reverse=True)[:per_page]
        files_paginated = None
    else:
        files_paginated = file_service.get_all_files_in_category(
            FileCategory.UPLOADS, page_nr, per_page)
        files = files_paginated.items

    form = FileForm()

    can_write = role_service.user_has_role(current_user, Roles.FILE_WRITE)

    return render_template('files/list.htm', files=files, form=form,
                           files_paginated=files_paginated, search=search,
                           can_write=can_write)


@blueprint.route('/', methods=['POST'])
@blueprint.route('/<int:page_nr>/', methods=['POST'])
@require_role(Roles.FILE_WRITE)
def upload(page_nr=1):
    """Upload a file."""
    new_files = []
    for new_file in request.files.getlist('file'):
        # File upload request, but no added files
        if new_file.filename == '':
            flash("No files selected", 'danger')
            return redirect(url_for('.list', page_nr=page_nr))

        f = file_service.add_file(FileCategory.UPLOADS, new_file,
                                  new_file.filename)
        new_files.append(f)

    files_paginated = file_service.get_all_files_in_category(
        FileCategory.UPLOADS, page_nr, 30)
    files = files_paginated.items

    form = FileForm()

    can_write = role_service.user_has_role(current_user, Roles.FILE_WRITE)

    return render_template('files/list.htm', files=files, form=form,
                           files_paginated=files_paginated, search=None,
                           new_files=new_files, can_write=can_write)


@blueprint.route('/content/<int:file_id>/<string:file_hash>/', methods=['GET'])
def content(file_id, file_hash):
    f = file_service.get_file_by_id(file_id)

    if f.hash != file_hash:
        return abort(404)

    if (f.category == FileCategory.EXAMINATION or
            f.category == FileCategory.ALV_DOCUMENT) and \
            (current_user.is_anonymous or not current_user.has_paid):
        return abort(404)

    mimetype = file_service.get_file_mimetype(f)
    content = file_service.get_file_content(f)

    headers = {'Content-Type': mimetype}

    if f.full_display_name is not None:
        headers['Content-Disposition'] = 'inline; filename="{}"'.format(
            f.full_display_name)

    return content, headers
