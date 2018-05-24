import unittest
from unittest import mock
from unittest.mock import patch

from app.service import pdf_service
from app.models.user import User


@patch.object(pdf_service, "user_service", autospec=True)
class TestPDFService(unittest.TestCase):

    def test_generate_pdf(self, user_service_mock):

        # Create the mock user to generate the pdf of
        mock_user = mock.Mock(first_name="Test",
                              last_name="Tester",
                              email="mailadres@svia.nl",
                              student_id="12345678",
                              spec_set=dir(User))
        user_service_mock.find_by_id.return_value = mock_user

        pdf_bytes = pdf_service.user_discount_card(1)
        user_service_mock.find_by_id.assert_called_once_with(1)

        # Check if all the user info appears in the generated pdf
        self.assertTrue(bytes(mock_user.first_name, "utf-8") in pdf_bytes)
        self.assertTrue(bytes(mock_user.last_name, "utf-8") in pdf_bytes)
        self.assertTrue(bytes(mock_user.student_id, "utf-8") in pdf_bytes)
        self.assertTrue(bytes("mailadres", "utf-8") in pdf_bytes)
        self.assertTrue(bytes("svia", "utf-8") in pdf_bytes)


if __name__ == '__main__':
    unittest.main()
