from flask_babel import _

from app.repository import alv_repository
from app.utils import file
from app.views.errors import ResourceNotFoundException


def save_alv(alv):
    alv_repository.save(alv)


def find_alv_by_id(alv_id, include_presidium, include_documents):
    return alv_repository.find_alv_by_id(alv_id,
                                         include_presidium=include_presidium,
                                         include_documents=include_documents)


def get_alv_by_id(alv_id, include_presidium=True, include_documents=False):
    alv = find_alv_by_id(alv_id, include_presidium, include_documents)
    if not alv:
        raise ResourceNotFoundException("alv", alv_id)
    return alv


def find_alv_document_by_id(alv_document_id):
    return alv_repository.find_alv_document_by_id(alv_document_id)


def get_alv_document_by_id(alv_document_id):
    alv_document = find_alv_document_by_id(alv_document_id)
    if not alv_document:
        raise ResourceNotFoundException("alv document", alv_document_id)
    return alv_document


def format_presidium(alv):
    if not alv.chairman and not alv.secretary:
        return _("No presidium")

    rv = []

    if alv.chairman:
        rv.append(str(alv.chairman))
    if alv.secretary:
        rv.append(str(alv.secretary))

    return _("Presidium: ") + ", ".join(rv)


def add_document(alv, file_storage, nl_name, en_name):
    alv_document = alv_repository.create_document()
    alv_document.alv = alv
    alv_document.en_name = en_name
    alv_document.nl_name = nl_name

    add_document_version(alv_document, file_storage)

    alv_repository.save_document(alv_document)


def add_document_version(alv_document, file_storage):
    _file = file.file_upload(file_storage)

    alv_doc_version = alv_repository.create_document_version()
    alv_doc_version.alv_document = alv_document
    alv_doc_version.file = _file

    alv_repository.save_document_version(alv_doc_version)


def update_document(alv_document, file_storage, nl_name, en_name):
    """Update a ALV document's names and add a new version."""
    alv_document.nl_name = nl_name
    alv_document.en_name = en_name

    if file_storage:
        add_document_version(alv_document, file_storage)

    alv_repository.save_document(alv_document)


def delete_alv(alv):
    alv_repository.delete_alv(alv)
