import unittest
from unittest import mock
from unittest.mock import patch

from app.enums import FileCategory
from app.exceptions import ResourceNotFoundException
from app.models.alv_model import Alv
from app.service import alv_service

alv_repository_mock = mock.MagicMock()
file_service_mock = mock.MagicMock()


@patch.object(alv_service, "file_service", file_service_mock)
@patch.object(alv_service, 'alv_repository', alv_repository_mock)
class TestAlvService(unittest.TestCase):

    def setUp(self):
        file_service_mock.reset_mock()
        alv_repository_mock.reset_mock()

    def test_save_alv(self):
        alv = mock.MagicMock()

        alv_service.save_alv(alv)

        alv_repository_mock.save.assert_called_once_with(alv)

    def test_find_all_alv(self):
        alv_service.find_all_alv()
        alv_repository_mock.find_all_alv.assert_called_once()

    def test_find_alv_by_id(self):
        alv_service.find_alv_by_id(1, False, False)

        alv_repository_mock.find_alv_by_id.assert_called_once_with(
            1, include_presidium=False, include_documents=False)

    def test_get_alv_by_id(self):

        alv_service.get_alv_by_id(1)

        alv_repository_mock.find_alv_by_id.assert_called_once_with(
            1, include_presidium=True, include_documents=False)

    def test_find_alv_document_by_id(self):
        alv_service.find_alv_document_by_id(1, True)

        alv_repository_mock.find_alv_document_by_id. \
            assert_called_once_with(1, True)

    def test_get_alv_document_by_id(self):
        alv_service.get_alv_document_by_id(1)

        alv_repository_mock.find_alv_document_by_id. \
            assert_called_once_with(1, False)

    def test_get_alv_document_by_id_not_found(self):
        alv_repository_mock.find_alv_document_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            alv_service.get_alv_document_by_id(1)

        alv_repository_mock.find_alv_document_by_id. \
            assert_called_once_with(1, False)

    def test_add_minutes(self):
        alv = mock.MagicMock(spec=dir(Alv))
        minutes_file = mock.MagicMock()
        minutes_file.filename = "minutes.pdf"

        alv_service.add_minutes(alv, minutes_file)

        file_service_mock.add_file.assert_called_once_with(
            FileCategory.ALV_DOCUMENT, minutes_file, minutes_file.filename)

    def test_add_document(self):
        alv = mock.MagicMock()
        file_storage = mock.MagicMock()
        file_storage.filename = "document.pdf"

        alv_service.add_document(alv, file_storage, "nl", "en")

        alv_repository_mock.create_document.assert_called_once_with()
        alv_repository_mock.save_document_version.assert_called_once()
        alv_repository_mock.save_document.assert_called_once()
        file_service_mock.add_file.assert_called_with(
            FileCategory.ALV_DOCUMENT, file_storage, file_storage.filename)

        created_mock = alv_repository_mock.create_document.return_value

        self.assertEqual(created_mock.alv, alv)
        self.assertEqual(created_mock.nl_name, "nl")
        self.assertEqual(created_mock.en_name, "en")

    def test_get_alv_by_id_not_found(self):
        alv_repository_mock.find_alv_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            alv_service.get_alv_by_id(1)

        alv_repository_mock.find_alv_by_id.assert_called_once_with(
            1, include_presidium=True, include_documents=False)

    def test_update_document(self):
        doc = mock.MagicMock()
        alv_service.update_document(doc, None, "nl", "en")

        alv_repository_mock.save_document.assert_called_once()
        alv_repository_mock.save_document_version.assert_not_called()
        file_service_mock.add_file.assert_not_called()

        self.assertEqual(doc.nl_name, "nl")
        self.assertEqual(doc.en_name, "en")

    def test_update_document_with_file_storage(self):
        doc = mock.MagicMock()
        file_storage = mock.MagicMock()
        file_storage.filename = "updated_document.pdf"

        alv_service.update_document(doc, file_storage, "nl", "en")

        alv_repository_mock.save_document.assert_called_once()
        alv_repository_mock.save_document_version.assert_called_once()
        file_service_mock.add_file.assert_called_with(
            FileCategory.ALV_DOCUMENT, file_storage, file_storage.filename)

        self.assertEqual(doc.nl_name, "nl")
        self.assertEqual(doc.en_name, "en")

    def test_delete_alv(self):
        alv = mock.MagicMock()

        alv_service.delete_alv(alv)

        alv_repository_mock.delete_alv.assert_called_once_with(alv)
