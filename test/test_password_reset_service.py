import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.exceptions import ResourceNotFoundException
from app.models.request_ticket import PasswordTicket
from app.models.user import User
from app.repository import password_reset_repository
from app.service import password_reset_service, mail_service, user_service

repository_mock = MagicMock(password_reset_repository)
mail_service_mock = MagicMock(mail_service)
user_service_mock = MagicMock(user_service)


@patch.object(password_reset_service, 'password_reset_repository',
              repository_mock)
@patch.object(password_reset_service, 'user_service', user_service_mock)
@patch.object(password_reset_service, 'mail_service', mail_service_mock)
class TestPasswordResetService(unittest.TestCase):

    def setUp(self):
        repository_mock.reset_mock()
        mail_service_mock.reset_mock()
        user_service_mock.reset_mock()

    def test_build_hash(self):
        hash_ = password_reset_service.build_hash(10)
        self.assertEqual(len(hash_), 10)
        hash_ = password_reset_service.build_hash(0)
        self.assertEqual(len(hash_), 0)
        hash_ = password_reset_service.build_hash(-1)
        self.assertEqual(len(hash_), 0)

    def test_get_valid_ticket(self):
        ticket = MagicMock(spec=PasswordTicket)
        ticket.created = datetime.now() - timedelta(minutes=15)
        repository_mock.find_password_ticket_by_hash.return_value = ticket

        rv = password_reset_service.get_valid_ticket("hash")

        repository_mock.find_password_ticket_by_hash\
            .assert_called_once_with("hash")

        self.assertEqual(ticket, rv)

    def test_get_valid_ticket_expired(self):
        ticket = MagicMock(spec=PasswordTicket)
        ticket.created = datetime.now() - timedelta(hours=1, minutes=1)
        repository_mock.find_password_ticket_by_hash.return_value = ticket

        with self.assertRaises(ResourceNotFoundException):
            password_reset_service.get_valid_ticket("hash")

    def test_get_valid_ticket_not_found(self):
        repository_mock.find_password_ticket_by_hash.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            password_reset_service.get_valid_ticket("hash")

    def test_reset_password(self):
        ticket = MagicMock(spec=PasswordTicket)

        password_reset_service.reset_password(ticket, "password")

        user_service_mock.set_password.\
            assert_called_once_with(ticket.user_id, "password")

    def test_create_password_ticket(self):
        # Facts
        email = "example@svia.nl"
        name = "John Doe"
        template = "email/forgot_password.html"

        # Setup
        user = MagicMock(spec=User)
        user.id.return_value = 1
        user.email.return_value = email
        user.name.return_value = name
        user_service_mock.get_user_by_email.return_value = user

        # Call
        password_reset_service.create_password_ticket(email)

        # Check
        user_service_mock.get_user_by_email.assert_called_once_with(email)
        repository_mock.create_password_ticket.assert_called_once()
        repository_mock.save.assert_called_once_with(
            repository_mock.create_password_ticket.return_value)
        mail_service_mock.send_mail.assert_called_once()

        args, kwargs = mail_service_mock.send_mail.call_args
        self.assertEqual(email, kwargs['to'].return_value)
        self.assertEqual(name, kwargs['user_name'].return_value)
        self.assertEqual(template, kwargs['email_template'])
