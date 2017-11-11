import unittest
from unittest import mock
from unittest.mock import patch

from requests import Session

from app.service import gitlab_service

gitlab_repository_mock = mock.MagicMock()


@patch.object(gitlab_service, 'gitlab_repository', gitlab_repository_mock)
class TestGitlabService(unittest.TestCase):

    def setUp(self):
        gitlab_repository_mock.reset_mock()

    def test_create_gitlab_session(self):
        token = "abc"

        session = gitlab_service.create_gitlab_session(token)

        self.assertIsInstance(session, Session)
        self.assertIn('PRIVATE-TOKEN', session.headers)
        self.assertIn(token, session.headers.values())

    def test_create_gitlab_issue(self):
        summary = "summary"
        user_email = "user_email"
        description = "description"

        gitlab_service.create_gitlab_issue(summary, user_email, description)

        gitlab_repository_mock.create_gitlab_issue.assert_called_once()
        (s, data), _ = gitlab_repository_mock.create_gitlab_issue.call_args
        self.assertIsInstance(s, Session)
        self.assertIn('title', data)
        self.assertIn('description', data)
        self.assertIn('labels', data)
        self.assertEqual(data['title'], summary)
        self.assertIn(user_email, data['description'])
        self.assertIn(description, data['description'])
