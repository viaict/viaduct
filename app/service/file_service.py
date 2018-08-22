import io
import mimetypes
import re
import logging

from PIL import Image
from fuzzywuzzy import fuzz
from werkzeug.utils import secure_filename

from app import hashfs
from app.enums import FileCategory
from app.exceptions import ResourceNotFoundException
from app.repository import file_repository

FILENAME_REGEX = re.compile(r'(.+)\.([^\s.]+)')

_logger = logging.getLogger(__name__)


def add_file(category, data, filename):
    m = FILENAME_REGEX.match(filename)
    if not m:
        orig_display_name = filename
        extension = ""
    else:
        orig_display_name = m.group(1)
        extension = m.group(2)

    if category == FileCategory.UPLOADS:
        display_name = orig_display_name
        filename_unique = False
        i = 0

        # Create a unique full display name
        while not filename_unique:
            i += 1
            duplicate = file_repository.find_file_by_display_name(
                display_name, extension)
            if duplicate is not None:
                display_name = "{}_{}".format(orig_display_name, i)
            else:
                filename_unique = True
    else:
        display_name = None

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
    try:
        with hashfs.open(_file.hash) as f:
            content = f.read()

        return content
    except IOError:
        raise ResourceNotFoundException('file content', _file.hash)


def get_image_with_headers(_file, display_name, picture_type='normal'):
    """
    Get the specified file as an image.

    Returns a tuple with the file content and headers, which can
    be immediately returned in a Flask view function.

    A thumbnail version of the image is returned when picture_type is equal
    to 'thumbnail'

    :param _file: file to load, a File model.
    :param display_name: When picture_type is not 'thumbnail', the user-visible
    name of the image.
    :param picture_type: either 'normal' or 'thumbnail'. When equal to
    'thumbnail', returns a thumbnail version of the image.
    :return: a tuple with both the image content and headers, which can be
    returned form a Flask view function.
    :raises: ResourceNotFoundException if there was an IOError loading the
    file.
    """

    if picture_type == 'normal':
        content = get_file_content(_file)
        headers = get_file_content_headers(_file, display_name)
    elif picture_type == 'thumbnail':
        content = get_thumbnail_of_file(_file)
        headers = {
            'Content-Type': mimetypes.types_map['.jpg']
        }
    else:
        raise Exception()

    return content, headers


def get_thumbnail_of_file(_file, thumbnail_size=None):
    if not thumbnail_size:
        thumbnail_size = (400, 400)

    try:
        with hashfs.open(_file.hash) as f:
            im = Image.open(f)

            im = im.convert("RGB")
            im.thumbnail(thumbnail_size)

            out = io.BytesIO()
            im.save(out, format='jpeg')
            return out.getvalue()
    except IOError:
        _logger.error('Error processing thumbnail', exc_info=True)
        raise ResourceNotFoundException('file content', _file.hash)


def get_file_mimetype(_file, add_http_text_charset='utf-8'):
    try:
        mimetype = mimetypes.types_map['.' + _file.extension]
        if mimetype.startswith('text/') and add_http_text_charset is not None:
            mimetype += '; charset=' + add_http_text_charset

        return mimetype
    except KeyError:
        return 'application/octet-stream'


def get_file_content_headers(_file, display_name=None):
    mimetype = get_file_mimetype(_file)

    headers = {'Content-Type': mimetype}

    if display_name is None:
        filename = _file.full_display_name
    else:
        filename = secure_filename(display_name)
        if len(_file.extension) > 0:
            filename += "." + _file.extension

    if filename is not None:
        headers['Content-Disposition'] = 'inline; filename="{}"'.format(
            filename)

    return headers


def get_all_files_in_category(category, page_nr=None, per_page=None):
    return file_repository.find_all_files_by_category(category,
                                                      page_nr, per_page)


def get_all_files(page_nr=None, per_page=None):
    return file_repository.find_all_files(page_nr, per_page)


def search_files_in_uploads(search):
    search = search.lower()
    all_files = get_all_files_in_category(FileCategory.UPLOADS)
    file_scores = {}

    for f in all_files:
        score = fuzz.partial_ratio(search, f.full_display_name.lower())
        if score > 75:
            file_scores[f] = score

    files = sorted(file_scores, key=file_scores.get, reverse=True)
    return files
