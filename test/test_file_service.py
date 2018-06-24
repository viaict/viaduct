import unittest
from io import StringIO
from unittest.mock import patch, MagicMock, call, Mock

from PIL import Image
from hashfs import HashAddress

from app import hashfs
from app.enums import FileCategory
from app.exceptions import ResourceNotFoundException
from app.models.file import File
from app.repository import file_repository
from app.service import file_service

file_repository_mock = MagicMock(spec=dir(file_repository))
hashfs_mock = MagicMock(spec=dir(hashfs))
pil_image_mock = MagicMock(spec=dir(Image))


def search_test_case(filenames, search,
                     expect_in_result,
                     expect_ordering=None):
    files = []

    for i, fn in enumerate(filenames):
        [display_name, extension] = fn.split('.')
        category = FileCategory.UPLOADS

        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        _file = MagicMock(spec=dir(File))
        _file.id = i + 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        _file.full_display_name = fn

        files.append(_file)

    file_repository_mock.find_all_files_by_category.return_value = files

    search_results = file_service.search_files_in_uploads(search)

    search_results_filenames = [r.full_display_name
                                for r in search_results]

    expect_in_result = set(expect_in_result)
    for fn in filenames:
        if fn in expect_in_result:
            assert fn in search_results_filenames, fn
        else:
            assert fn not in search_results_filenames, fn

    if expect_ordering:

        # Test if we have the same ordering in the result
        prev_index = -1

        for fn in expect_ordering:
            assert fn in expect_in_result, fn

            index = search_results_filenames.index(fn)
            assert index > prev_index, fn
            prev_index = index


@patch.object(file_service, 'file_repository', file_repository_mock)
@patch.object(file_service, 'hashfs', hashfs_mock)
@patch.object(file_service, 'Image', pil_image_mock)
class TestFileService(unittest.TestCase):

    def setUp(self):
        file_repository_mock.reset_mock()
        hashfs_mock.reset_mock()

    def test_file_full_display_name(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        expected_full_display_name = display_name + '.' + extension

        f = MagicMock(spec=dir(File))
        f.display_name = display_name
        f.extension = extension
        f.hash = '123456789abcdefghiklmnopqrstuvwxyz'
        f.category = FileCategory.UPLOADS

        # == Property __get__ call ==

        full_display_name = File.full_display_name.__get__(f)

        # == Assertions

        self.assertEqual(expected_full_display_name, full_display_name)

    def test_file_full_display_name_no_extension(self):
        # === Initialization ===

        display_name = 'test123'
        extension = ''
        expected_full_display_name = display_name

        # == Property __get__ call ==

        f = MagicMock(spec=dir(File))
        f.display_name = display_name
        f.extension = extension
        f.hash = '123456789abcdefghiklmnopqrstuvwxyz'
        f.category = FileCategory.UPLOADS

        full_display_name = File.full_display_name.__get__(f)

        # == Assertions

        self.assertEqual(expected_full_display_name, full_display_name)

    def test_file_full_display_name_no_display_name(self):
        # === Initialization ===

        display_name = None
        extension = 'png'
        expected_full_display_name = None

        # == Property __get__ call ==

        f = MagicMock(spec=dir(File))
        f.display_name = display_name
        f.extension = extension
        f.hash = '123456789abcdefghiklmnopqrstuvwxyz'
        f.category = FileCategory.ACTIVITY_PICTURE

        full_display_name = File.full_display_name.__get__(f)

        # == Assertions

        self.assertEqual(expected_full_display_name, full_display_name)

    def test_add_file_uploads(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        data = StringIO('test data')
        category = FileCategory.UPLOADS

        # === Set return values ===

        expected_file = MagicMock(spec=dir(File))
        expected_address = MagicMock(spec=dir(HashAddress))
        expected_address.id = '123456789abcdefghiklmnopqrstuvwxyz'

        filename = '{}.{}'.format(display_name, extension)

        file_repository_mock.create_file.return_value = expected_file

        # Assume no duplicate display name
        file_repository_mock.find_file_by_display_name.return_value = None
        hashfs_mock.put.return_value = expected_address

        # === Service function call ===

        _file = file_service.add_file(category, data, filename)

        # === Assertions ===

        self.assertEqual(_file, expected_file)

        self.assertEqual(expected_file.display_name, display_name)
        self.assertEqual(expected_file.extension, extension)
        self.assertEqual(expected_file.category, category)
        self.assertEqual(expected_file.hash, expected_address.id)

        hashfs_mock.put.assert_called_once_with(data)
        file_repository_mock.create_file.assert_called_once()
        file_repository_mock.find_file_by_display_name.assert_called_once_with(
            display_name, extension)
        file_repository_mock.save.assert_called_once_with(_file)

    def test_add_file_uploads_duplicate_display_name(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        data = StringIO('test data')
        category = FileCategory.UPLOADS

        # === Set return values ===

        expected_file = MagicMock(spec=dir(File))
        expected_address = MagicMock(spec=dir(HashAddress))
        expected_address.id = '123456789abcdefghiklmnopqrstuvwxyz'

        filename = '{}.{}'.format(display_name, extension)

        file_repository_mock.create_file.return_value = expected_file

        duplicate_file = MagicMock(spec=dir(File))
        duplicate_file.display_name = display_name
        duplicate_file.extension = extension

        # Assume duplicate display name
        def mock_find_file_by_display_name(d, e):
            if d == display_name and e == extension:
                return duplicate_file

            return None

        file_repository_mock.find_file_by_display_name.side_effect = \
            mock_find_file_by_display_name
        hashfs_mock.put.return_value = expected_address

        # === Service function call ===

        _file = file_service.add_file(category, data, filename)

        # === Assertions ===

        self.assertEqual(_file, expected_file)

        # Service should have changed the display name
        self.assertNotEqual(expected_file.display_name, display_name)

        # Service should add a suffix to the original display name
        assert expected_file.display_name.startswith(display_name)

        self.assertEqual(expected_file.extension, extension)
        self.assertEqual(expected_file.category, category)
        self.assertEqual(expected_file.hash, expected_address.id)

        hashfs_mock.put.assert_called_once_with(data)
        file_repository_mock.create_file.assert_called_once()

        # Calls to find_file_by_display_name

        find_file_by_display_name_calls = [
            call(display_name, extension),
            call(expected_file.display_name, extension)]

        self.assertEqual(
            file_repository_mock.find_file_by_display_name.call_args_list,
            find_file_by_display_name_calls)

        file_repository_mock.save.assert_called_once_with(_file)

    def test_add_file_uploads_no_extension(self):
        # === Initialization ===

        display_name = 'test123'
        extension = ''
        data = StringIO('test data')
        category = FileCategory.UPLOADS

        # === Set return values ===

        expected_file = MagicMock(spec=dir(File))
        expected_address = MagicMock(spec=dir(HashAddress))
        expected_address.id = '123456789abcdefghiklmnopqrstuvwxyz'

        filename = display_name

        file_repository_mock.create_file.return_value = expected_file

        # Assume no duplicate display name
        file_repository_mock.find_file_by_display_name.return_value = None
        hashfs_mock.put.return_value = expected_address

        # === Service function call ===

        _file = file_service.add_file(category, data, filename)

        # === Assertions ===

        self.assertEqual(_file, expected_file)

        self.assertEqual(expected_file.display_name, display_name)
        self.assertEqual(expected_file.extension, extension)
        self.assertEqual(expected_file.category, category)
        self.assertEqual(expected_file.hash, expected_address.id)

        hashfs_mock.put.assert_called_once_with(data)
        file_repository_mock.create_file.assert_called_once()
        file_repository_mock.find_file_by_display_name.assert_called_once_with(
            display_name, extension)
        file_repository_mock.save.assert_called_once_with(_file)

    def test_add_file_other_category(self):
        # === Initialization ===

        filename = 'test123.png'
        data = StringIO('test data')
        category = FileCategory.ACTIVITY_PICTURE

        # === Set return values ===

        expected_file = MagicMock(spec=dir(File))
        expected_address = MagicMock(spec=dir(HashAddress))
        expected_address.id = '123456789abcdefghiklmnopqrstuvwxyz'

        file_repository_mock.create_file.return_value = expected_file

        # Assume no duplicate display name
        file_repository_mock.find_file_by_display_name.return_value = None
        hashfs_mock.put.return_value = expected_address

        # === Service function call ===

        _file = file_service.add_file(category, data, filename)

        # === Assertions ===

        self.assertEqual(_file, expected_file)

        self.assertEqual(expected_file.display_name, None)
        self.assertEqual(expected_file.extension, 'png')
        self.assertEqual(expected_file.category, category)
        self.assertEqual(expected_file.hash, expected_address.id)

        hashfs_mock.put.assert_called_once_with(data)
        file_repository_mock.create_file.assert_called_once()
        file_repository_mock.find_file_by_display_name.assert_not_called()
        file_repository_mock.save.assert_called_once_with(_file)

    def test_delete_file_no_duplicates(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Set return values ===

        file_repository_mock.find_all_files_by_hash.return_value = []

        # === Service function call ===

        file_service.delete_file(_file)

        # === Assertions ===

        file_repository_mock.delete.assert_called_once_with(_file)
        file_repository_mock.find_all_files_by_hash \
            .assert_called_once_with(_hash)
        hashfs_mock.delete.assert_called_once_with(_hash)

    def test_delete_file_with_duplicates(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Set return values ===

        duplicate_file = MagicMock(spec=dir(File))
        duplicate_file.id = 2
        duplicate_file.hash = _hash
        duplicate_file.category = category
        duplicate_file.display_name = display_name + "_1"
        duplicate_file.extension = extension

        file_repository_mock.find_all_files_by_hash.return_value = \
            [duplicate_file]

        # === Service function call ===

        file_service.delete_file(_file)

        # === Assertions ===

        file_repository_mock.delete.assert_called_once_with(_file)
        file_repository_mock.find_all_files_by_hash \
            .assert_called_once_with(_hash)
        hashfs_mock.delete.assert_not_called()

    def test_get_file_by_id(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        expected_file = MagicMock(spec=dir(File))
        expected_file.id = 1
        expected_file.hash = _hash
        expected_file.category = category
        expected_file.display_name = display_name
        expected_file.extension = extension

        # === Set return values ===

        file_repository_mock.find_file_by_id.return_value = expected_file

        # === Service function call ===

        _file = file_service.get_file_by_id(expected_file.id)

        # === Assertions ===

        self.assertEqual(expected_file, _file)

    def test_get_file_by_id_non_existing(self):
        # === Set return values ===

        file_repository_mock.find_file_by_id.return_value = None

        # === Service function call ===

        with self.assertRaises(ResourceNotFoundException):
            file_service.get_file_by_id(1)

    def test_get_file_content(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        data = '1eb55d09d99d4d0686581a7fdb8a3346'
        data_reader = StringIO(data)

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Set return values ===

        hashfs_mock.open.return_value = data_reader

        # === Service function call ===

        content = file_service.get_file_content(_file)

        # === Assertions ===

        self.assertEqual(data, content)

    def test_get_file_content_invalid_hash(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Set return values ===

        def mock_open(_hash):
            raise IOError()

        hashfs_mock.open.side_effect = mock_open

        # === Service function call ===

        with self.assertRaises(ResourceNotFoundException):
            file_service.get_file_content(_file)

        hashfs_mock.open.reset_mock(side_effect=True)

    def test_get_image_with_headers_normal(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Service function call ===

        with patch.object(file_service, 'get_file_content'):
            with patch.object(file_service, 'get_file_content_headers'):
                file_service.get_image_with_headers(_file, display_name,
                                                    'normal')
                file_service.get_file_content.assert_called_once()
                file_service.get_file_content_headers.assert_called_once()

    def test_get_image_with_headers_thumbnail(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Service function call ===

        with patch.object(file_service, 'get_thumbnail_of_file'):
            file_service.get_image_with_headers(_file, display_name,
                                                'thumbnail')
            file_service.get_thumbnail_of_file.assert_called_once()

    def test_get_thumbnail_of_file(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        data = '1eb55d09d99d4d0686581a7fdb8a3346'
        data_reader = StringIO(data)

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Set return values ===

        hashfs_mock.open.return_value = data_reader

        pil_img = Mock()

        pil_image_mock.open.return_value = pil_img

        # === Service function call ===

        with_size = (567, 765)

        file_service.get_thumbnail_of_file(
            _file, thumbnail_size=with_size)

        # === Assertions ===

        pil_img.thumbnail.assert_called_once_with(with_size)
        pil_img.save.assert_called_once()

    def test_get_file_mimetype_png(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        expected_mimetype = 'image/png'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Service function call ===

        mimetype = file_service.get_file_mimetype(_file)

        # === Assertions ===

        self.assertEqual(mimetype, expected_mimetype)

    def test_get_file_mimetype_txt(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'txt'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        expected_mimetype = 'text/plain'
        expected_mimetype_charset = 'text/plain; charset=utf-8'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Service function call ===

        mimetype = file_service.get_file_mimetype(
            _file, add_http_text_charset=None)
        mimetype_charset = file_service.get_file_mimetype(_file)

        # === Assertions ===

        self.assertEqual(mimetype, expected_mimetype)
        self.assertEqual(mimetype_charset, expected_mimetype_charset)

    def test_get_file_mimetype_unknown(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'noidea'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        expected_mimetype = 'application/octet-stream'

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension

        # === Service function call ===

        mimetype = file_service.get_file_mimetype(_file)

        # === Assertions ===

        self.assertEqual(mimetype, expected_mimetype)

    def test_get_file_content_headers(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        full_display_name = display_name + "." + extension

        expected_content_type = "image/png"
        expected_content_disposition = 'inline; filename="{}"'.format(
            full_display_name)

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension
        _file.full_display_name = full_display_name

        # === Service function call ===

        with patch.object(file_service, 'get_file_mimetype',
                          return_value=expected_content_type):
            headers = file_service.get_file_content_headers(_file)

        # === Assertions ===

        assert "Content-Type" in headers
        assert "Content-Disposition" in headers

        self.assertEqual(headers["Content-Type"], expected_content_type)
        self.assertEqual(headers["Content-Disposition"],
                         expected_content_disposition)

    def test_get_file_content_headers_no_display_name(self):
        # === Initialization ===

        display_name = None
        extension = 'png'
        category = FileCategory.ACTIVITY_PICTURE
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        full_display_name = None

        expected_content_type = "image/png"

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension
        _file.full_display_name = full_display_name

        # === Service function call ===

        with patch.object(file_service, 'get_file_mimetype',
                          return_value=expected_content_type):
            headers = file_service.get_file_content_headers(_file)

        # === Assertions ===

        assert "Content-Type" in headers
        assert "Content-Disposition" not in headers

        self.assertEqual(headers["Content-Type"], expected_content_type)

    def test_get_file_content_headers_explicit_display_name(self):
        # === Initialization ===

        display_name = None
        extension = 'png'
        category = FileCategory.ACTIVITY_PICTURE
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        full_display_name = None

        overriden_display_name = 'test456'

        expected_content_type = "image/png"
        expected_content_disposition = 'inline; filename="{}.{}"'.format(
            overriden_display_name, extension)

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension
        _file.full_display_name = full_display_name

        # === Service function call ===

        with patch.object(file_service, 'get_file_mimetype',
                          return_value=expected_content_type):
            headers = file_service.get_file_content_headers(
                _file, display_name=overriden_display_name)

        # === Assertions ===

        assert "Content-Type" in headers
        assert "Content-Disposition" in headers

        self.assertEqual(headers["Content-Type"], expected_content_type)
        self.assertEqual(headers["Content-Disposition"],
                         expected_content_disposition)

    def test_get_file_content_headers_override_display_name(self):
        # === Initialization ===

        display_name = 'test123'
        extension = 'png'
        category = FileCategory.UPLOADS
        _hash = '123456789abcdefghiklmnopqrstuvwxyz'
        full_display_name = display_name + "." + extension

        overriden_display_name = 'test456'

        expected_content_type = "image/png"
        expected_content_disposition = 'inline; filename="{}.{}"'.format(
            overriden_display_name, extension)

        _file = MagicMock(spec=dir(File))
        _file.id = 1
        _file.hash = _hash
        _file.category = category
        _file.display_name = display_name
        _file.extension = extension
        _file.full_display_name = full_display_name

        # === Service function call ===

        with patch.object(file_service, 'get_file_mimetype',
                          return_value=expected_content_type):
            headers = file_service.get_file_content_headers(
                _file, display_name=overriden_display_name)

        # === Assertions ===

        assert "Content-Type" in headers
        assert "Content-Disposition" in headers

        self.assertEqual(headers["Content-Type"], expected_content_type)
        self.assertEqual(headers["Content-Disposition"],
                         expected_content_disposition)

    def test_get_all_files_in_category(self):
        # === Initialization ===

        files_uploads = []
        files_activity_pictures = []

        find_category = FileCategory.ACTIVITY_PICTURE
        find_category_empty = FileCategory.ALV_DOCUMENT

        for i in range(10):
            if i < 5:
                category = FileCategory.UPLOADS
                display_name = 'test{}'.format(i)
            else:
                category = FileCategory.ACTIVITY_PICTURE
                display_name = None

            extension = 'png'
            _hash = '123456789abcdefghiklmnopqrstuvwxyz'

            _file = MagicMock(spec=dir(File))
            _file.id = i + 1
            _file.hash = _hash
            _file.category = category
            _file.display_name = display_name
            _file.extension = extension

            if category == FileCategory.UPLOADS:
                files_uploads.append(_file)
            else:
                files_activity_pictures.append(_file)

        # === Test with category with files ===

        file_repository_mock.find_all_files_by_category.return_value = \
            files_activity_pictures

        result = file_service.get_all_files_in_category(find_category)

        self.assertEqual(set(result), set(files_activity_pictures))
        file_repository_mock.find_all_files_by_category \
            .assert_called_once_with(find_category, None, None)

        # === Test with empty category ===

        file_repository_mock.find_all_files_by_category.return_value = []

        result = file_service.get_all_files_in_category(find_category_empty)

        self.assertEqual(len(result), 0)
        file_repository_mock.find_all_files_by_category \
            .assert_called_with(find_category_empty, None, None)

    def test_get_all_files_in_category_with_pages(self):
        # === Initialization ===

        files_uploads = []
        files_activity_pictures = []

        find_category = FileCategory.ACTIVITY_PICTURE

        page_nr = 2
        per_page = 3

        for i in range(10):
            if i < 5:
                category = FileCategory.UPLOADS
                display_name = 'test{}'.format(i)
            else:
                category = FileCategory.ACTIVITY_PICTURE
                display_name = None

            extension = 'png'
            _hash = '123456789abcdefghiklmnopqrstuvwxyz'

            _file = MagicMock(spec=dir(File))
            _file.id = i + 1
            _file.hash = _hash
            _file.category = category
            _file.display_name = display_name
            _file.extension = extension

            if category == FileCategory.UPLOADS:
                files_uploads.append(_file)
            else:
                files_activity_pictures.append(_file)

        expected_result = files_activity_pictures[
                          per_page * (page_nr - 1):per_page * page_nr]

        # === Set return values ===

        file_repository_mock.find_all_files_by_category.return_value = \
            expected_result

        # === Service function call ===

        result = file_service.get_all_files_in_category(
            find_category, page_nr=page_nr, per_page=per_page)

        # === Assertions ===

        self.assertEqual(set(result), set(expected_result))
        file_repository_mock.find_all_files_by_category \
            .assert_called_with(find_category, page_nr, per_page)

    def test_get_all_files(self):
        files_uploads = []
        files_activity_pictures = []

        for i in range(10):
            if i < 5:
                category = FileCategory.UPLOADS
                display_name = 'test{}'.format(i)
            else:
                category = FileCategory.ACTIVITY_PICTURE
                display_name = None

            extension = 'png'
            _hash = '123456789abcdefghiklmnopqrstuvwxyz'

            _file = MagicMock(spec=dir(File))
            _file.id = i + 1
            _file.hash = _hash
            _file.category = category
            _file.display_name = display_name
            _file.extension = extension

            if category == FileCategory.UPLOADS:
                files_uploads.append(_file)
            else:
                files_activity_pictures.append(_file)

        expected_result = files_uploads + files_activity_pictures

        # === Set return values ===

        file_repository_mock.find_all_files.return_value = expected_result

        # === Service function call ===

        result = file_service.get_all_files()

        # === Assertions ===

        self.assertEqual(set(result), set(expected_result))
        file_repository_mock.find_all_files.assert_called_with(None, None)

    def test_get_all_files_with_pages(self):
        files_uploads = []
        files_activity_pictures = []

        page_nr = 2
        per_page = 3

        for i in range(10):
            if i < 5:
                category = FileCategory.UPLOADS
                display_name = 'test{}'.format(i)
            else:
                category = FileCategory.ACTIVITY_PICTURE
                display_name = None

            extension = 'png'
            _hash = '123456789abcdefghiklmnopqrstuvwxyz'

            _file = MagicMock(spec=dir(File))
            _file.id = i + 1
            _file.hash = _hash
            _file.category = category
            _file.display_name = display_name
            _file.extension = extension

            if category == FileCategory.UPLOADS:
                files_uploads.append(_file)
            else:
                files_activity_pictures.append(_file)

        all_files = files_uploads + files_activity_pictures
        expected_result = all_files[
                          per_page * (page_nr - 1):per_page * page_nr]

        # === Set return values ===

        file_repository_mock.find_all_files.return_value = expected_result

        # === Service function call ===

        result = file_service.get_all_files(page_nr=page_nr, per_page=per_page)

        # === Assertions ===

        self.assertEqual(set(result), set(expected_result))
        file_repository_mock.find_all_files.assert_called_with(
            page_nr, per_page)

    def test_search_files_in_uploads_case_insensitive(self):
        filenames = ['ThEFiLeWheReIAmLookingFor.txt', 'bbb.txt',
                     'ccc.txt', 'ddd.png', 'eee.pdf']
        search = 'TheFileWhereiAmlookingFor'
        expect_in_result = ['ThEFiLeWheReIAmLookingFor.txt']

        search_test_case(filenames, search, expect_in_result)

    def test_search_files_in_uploads_extension(self):
        filenames = ['aaa.txt', 'bbb.png', 'ccc.pdf', 'ddd.html']
        search = 'pdf'
        expect_in_result = ['ccc.pdf']

        search_test_case(filenames, search, expect_in_result)

    def test_search_files_in_uploads_similarity_1(self):
        filenames = ['somethingelse.png', 'myfileisawesome.pdf',
                     'yourfileisawesome.pdf']

        search = 'myfileisawesome'
        expected_ordering = ['myfileisawesome.pdf', 'yourfileisawesome.pdf']

        search_test_case(filenames, search,
                         expected_ordering, expected_ordering)

    def test_search_files_in_uploads_similarity_2(self):
        filenames = ['abc.txt', 'abcd.txt', 'abcde.txt',
                     'abcdef.txt', 'xyz.txt', 'abbcdeef.txt']
        search = 'abcdef'
        expect_in_result = ['abcdef.txt', 'abcde.txt',
                            'abbcdeef.txt']
        expected_ordering = ['abcdef.txt', 'abcde.txt',
                             'abbcdeef.txt']

        search_test_case(filenames, search,
                         expect_in_result, expected_ordering)

    def test_search_files_in_uploads_similarity_3(self):
        filenames = ['file16.txt', 'file17.txt', 'file18.txt', 'asdasd19.txt']
        search = 'file18'
        expect_in_result = ['file16.txt', 'file17.txt', 'file18.txt']
        expected_ordering = ['file18.txt', 'file17.txt']

        search_test_case(filenames, search,
                         expect_in_result, expected_ordering)
