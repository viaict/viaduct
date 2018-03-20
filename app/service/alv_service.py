from app.enums import FileCategory
from app.repository import alv_repository
from app.views.errors import ResourceNotFoundException
from app.service import file_service

from werkzeug.utils import secure_filename


def save_alv(alv):
    alv_repository.save(alv)


def add_minutes(alv, minutes_file):
    _file = file_service.add_file(FileCategory.ALV_DOCUMENT,
                                  minutes_file, minutes_file.filename)
    alv.minutes_file_id = _file.id

    alv_repository.save(alv)


def find_all_alv():
    return alv_repository.find_all_alv()


def find_alv_by_id(alv_id, include_presidium, include_documents):
    return alv_repository.find_alv_by_id(alv_id,
                                         include_presidium=include_presidium,
                                         include_documents=include_documents)


def get_alv_by_id(alv_id, include_presidium=True, include_documents=False):
    alv = find_alv_by_id(alv_id, include_presidium, include_documents)
    if not alv:
        raise ResourceNotFoundException("alv", alv_id)
    return alv


def find_alv_document_by_id(alv_document_id, include_versions):
    return alv_repository.find_alv_document_by_id(
        alv_document_id, include_versions)


def get_alv_document_by_id(alv_document_id, include_versions=False):
    alv_document = find_alv_document_by_id(alv_document_id, include_versions)
    if not alv_document:
        raise ResourceNotFoundException("alv document", alv_document_id)
    return alv_document


def get_alv_document_version_filename(alv_document, version_number,
                                      _file, locale=None):

    basename = alv_document.get_localized_basename()

    fn = secure_filename(basename)
    if version_number > 1:
        fn += "_v{}".format(version_number)

    if len(_file.extension) > 0:
        fn += "." + _file.extension

    return fn


def get_alv_document_version_file(alv_document_version):
    _file = file_service.get_file_by_id(alv_document_version.file_id)
    return _file


def get_alv_minutes_file(alv):
    _file = file_service.get_file_by_id(alv.minutes_file_id)
    return _file


def get_alv_minutes_filename(alv, _file):
    basename = alv.get_localized_basename()

    fn = "{}_minutes".format(secure_filename(basename))

    if len(_file.extension) > 0:
        fn += "." + _file.extension

    return fn


def add_document(alv, file_storage, nl_name, en_name):
    alv_document = alv_repository.create_document()
    alv_document.alv = alv
    alv_document.en_name = en_name
    alv_document.nl_name = nl_name

    add_document_version(alv_document, file_storage)

    alv_repository.save_document(alv_document)


def add_document_version(alv_document, file_storage):
    _file = file_service.add_file(FileCategory.ALV_DOCUMENT,
                                  file_storage, file_storage.filename)

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
