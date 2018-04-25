import unittest
from unittest.mock import patch

from app.service import mail_service


@patch.object(mail_service, 'google', autospec=True)
class TestMailService(unittest.TestCase):

    def test_send_mail(self, google_mock):
        to = "to"
        subject = "subject"
        template = "sometemplate"
        template_kwargs = dict(a=1, b=2, c=3)

        mail_service.send_mail(to=to, subject=subject,
                               email_template=template, **template_kwargs)

        google_mock.send_email.assert_called_once_with(
            to, subject, template, email_template_kwargs=template_kwargs)
