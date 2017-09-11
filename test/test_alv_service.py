import unittest
from unittest import mock
from unittest.mock import patch


from app.service import alv_service
from app.exceptions import ResourceNotFoundException

alv_repository_mock = mock.MagicMock()
file_mock = mock.MagicMock()


@patch.object(alv_service, "file", file_mock)
@patch.object(alv_service, 'alv_repository', alv_repository_mock)
class TestAlvService(unittest.TestCase):

    def setUp(self):
        file_mock.reset_mock()
        alv_repository_mock.reset_mock()

    # @patch(alv_repo + "find_alv_by_id", ALV)
    def test_find_alv_by_id_found(self):
        alv_service.find_alv_by_id(1, False, False)

        alv_repository_mock.find_alv_by_id.assert_called_with(
            1, include_presidium=False, include_documents=False)

    def test_get_alv_by_id_not_found(self):
        alv_repository_mock.find_alv_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            alv_service.get_alv_by_id(1)

        alv_repository_mock.find_alv_by_id.assert_called_with(
            1, include_presidium=True, include_documents=False)
        alv_repository_mock.find_alv_by_id.assert_called_once()

    def test_update_document(self):
        doc = mock.MagicMock()
        alv_service.update_document(doc, None, "nl", "en")

        alv_repository_mock.save_document.assert_called_once()
        alv_repository_mock.save_document_version.assert_not_called()
        file_mock.file_upload.assert_not_called()

        self.assertEqual(doc.nl_name, "nl")
        self.assertEqual(doc.en_name, "en")

    def test_update_document_with_file_storage(self):
        doc = mock.MagicMock()
        file_storage = mock.MagicMock()

        alv_service.update_document(doc, file_storage, "nl", "en")

        alv_repository_mock.save_document.assert_called_once()
        alv_repository_mock.save_document_version.assert_called_once()
        file_mock.file_upload.assert_called_with(file_storage)
