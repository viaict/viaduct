from flask import Blueprint, abort, render_template, request, url_for, redirect
from flask_login import login_required

from app.forms.alv import AlvForm, AlvDocumentForm
from app.models.alv_model import Alv
from app.service import alv_service
from app.utils.module import ModuleAPI

blueprint = Blueprint('alv', __name__, url_prefix='/alv')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/list/', methods=['GET'])
@login_required
def list():
    if not ModuleAPI.can_read('alv'):
        return abort(403)

    alvs = alv_service.find_all_alv()
    return render_template('alv/list.htm', alvs=alvs)


@blueprint.route('/<int:alv_id>/', methods=['GET'])
@login_required
def view(alv_id=0):
    if not ModuleAPI.can_read('alv'):
        return abort(403)
    if alv_id:
        alv = alv_service.get_alv_by_id(alv_id, include_documents=True)

    return render_template('alv/view.htm', alv=alv)


@blueprint.route("/create/", methods=['GET', 'POST'])
@blueprint.route("/<int:alv_id>/edit/", methods=['GET', 'POST'])
@login_required
def create_edit(alv_id=None):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    if alv_id:
        alv = alv_service.get_alv_by_id(alv_id)
    else:
        alv = Alv()

    form = AlvForm(request.form, alv)

    if form.validate_on_submit():
        form.populate_obj(alv)
        alv_service.save_alv(alv)
        return redirect(url_for('alv.list'))

    return render_template('alv/edit.htm', form=form)


@blueprint.route('/<int:alv_id>/documents/create/', methods=['GET', 'POST'])
@login_required
def create_document(alv_id=None):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    alv = alv_service.get_alv_by_id(alv_id)
    form = AlvDocumentForm(request.form)

    if form.validate_on_submit() and form.file.id in request.files:
        alv_service.add_document(alv, request.files.get(form.file.id),
                                 form.nl_name.data, form.en_name.data)
        return redirect(url_for('alv.view', alv_id=alv.id))

    return render_template('alv/upload_document.htm', form=form, alv=alv)


@blueprint.route('/<int:alv_id>/documents/<int:doc_id>/update/',
                 methods=['GET', 'POST'])
@login_required
def update_document(alv_id=None, doc_id=None):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    alv = alv_service.get_alv_by_id(alv_id)
    alv_document = alv_service.get_alv_document_by_id(doc_id)

    form = AlvDocumentForm(request.form)
    form.nl_name.data = alv_document.nl_name
    form.en_name.data = alv_document.en_name

    if form.validate_on_submit():
        alv_service.update_document(
            alv_document,
            request.files.get(form.file.id, None),
            form.nl_name.data, form.en_name.data)
        return redirect(url_for('alv.view', alv_id=alv.id))

    return render_template('alv/upload_document.htm', form=form, alv=alv)


@blueprint.route('/<int:alv_id>/delete/', methods=['POST'])
@login_required
def delete(alv_id=None):
    if not ModuleAPI.can_write('alv'):
        return abort(403)

    alv = alv_service.get_alv_by_id(alv_id)
    alv_service.delete_alv(alv)

    return redirect(url_for('alv.list'))
