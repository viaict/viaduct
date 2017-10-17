import unittest
from unittest.mock import patch, MagicMock

from app.service import mail_service

google_mock = MagicMock()


@patch.object(mail_service, 'google', google_mock)
class TestMailService(unittest.TestCase):
    def setUp(self):
        google_mock.reset_mock()

    def test_send_mail(self):
        to = "to"
        subject = "subject"
        template = "sometemplate"

        mail_service.send_mail(to=to, subject=subject, email_template=template)

        google_mock.send_mail.assert_called_once_with(to, subject, template)
