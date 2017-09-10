import unittest
from unittest import mock
from unittest.mock import patch

from werkzeug.datastructures import FileStorage

from app.models.alv_model import AlvDocument
from app.service import alv_service

AlvDocumentMock = mock.Mock(AlvDocument)
FileStorageMock = mock.Mock(FileStorage)


@patch("app.repository.alv_repository.save_document_version")
@patch("app.repository.alv_repository.save_document")
@patch("app.utils.file.file_upload")
class TestAlvService(unittest.TestCase):
    def test_update_document(self, file_upload, save_document,
                             save_document_version):
        doc = AlvDocumentMock()

        alv_service.update_document(doc, None, "nl", "en")

        self.assertFalse(save_document_version.called)
        self.assertFalse(file_upload.called)
        self.assertTrue(save_document.called)

    @patch("app.models.alv_model.AlvDocumentVersion")
    def test_update_document_with_file_storage(self, file_upload,
                                               save_document,
                                               save_document_version,
                                               alv_doc_version):
        doc = AlvDocumentMock()
        file_storage = FileStorageMock()

        alv_service.update_document(doc, file_storage, "nl", "en")

        self.assertFalse(save_document_version.called)
        self.assertFalse(file_upload.called)
        self.assertTrue(save_document.called)
