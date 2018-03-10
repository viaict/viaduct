import mimetypes

from app import hashfs
from app.enums import FileCategory
from app.repository import file_repository
from app.exceptions import ResourceNotFoundException, \
    DuplicateResourceException, BusinessRuleException


def add_file(category, data, extension, display_name=None):
    if display_name is not None and category != FileCategory.UPLOADS:
        raise BusinessRuleException(
            'display_name is only allowed for category \'UPLOADS\'')
    elif display_name is None and category == FileCategory.UPLOADS:
        raise BusinessRuleException(
            'display_name is required for category \'UPLOADS\'')
    elif display_name is not None:
        duplicate = file_repository.find_file_by_display_name(display_name)
        if duplicate is not None:
            raise DuplicateResourceException(display_name, duplicate.id)

    address = hashfs.put(data)

    f = file_repository.create_file()
    f.display_name = display_name
    f.hash = address.id
    f.extension = extension
    f.category = category

    file_repository.save(f)

    return f


def delete_file(_file):
    _hash = _file.hash
    file_repository.delete(_file)
    if len(file_repository.find_all_files_by_hash(_hash)) == 0:
        hashfs.delete(_hash)


def get_file_by_id(file_id):
    f = file_repository.find_file_by_id(file_id)
    if not f:
        raise ResourceNotFoundException("file", file_id)
    return f


def get_file_content(_file):
    with hashfs.open(_file.hash) as f:
        content = f.read()

    return content


def get_file_mimetype(_file):
    try:
        return mimetypes.types_map['.' + _file.extension]
    except KeyError:
        return None


def get_all_files_in_category(category):
    return file_repository.find_all_files_by_category(category)


def get_all_files():
    return file_repository.find_all_files()
