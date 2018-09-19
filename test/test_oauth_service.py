import unittest
from flask_babel import LazyString
from unittest.mock import patch, MagicMock

from app.exceptions.base import ResourceNotFoundException, \
    BusinessRuleException
from app.models.oauth.client import OAuthClient
from app.models.oauth.token import OAuthToken
from app.repository import oauth_repository as mock_spec  # rename for safety
from app.service import oauth_service
from test import Any

oauth_repo_mock = MagicMock(spec=dir(mock_spec))
client_mock = MagicMock(OAuthClient)
token_mock = MagicMock(OAuthToken)

access_token = "access_token"
refresh_token = "refresh_token"
client_id = "client_id"
client_secret = "client_secret"
grant_code = "grant_code"
code = {"code": "grant_code"}
scopes = "SCOPE1 SCOPE2 SCOPE3"
scopes_list = ["SCOPE1", "SCOPE2", "SCOPE3"]
redirect_uri = "http://svia.nl"
token_type = "Bearer"
expires = 3600
user_id = 1
grant_id = 2


@patch.object(oauth_service, 'oauth_repository', oauth_repo_mock)
class TestOAuthService(unittest.TestCase):
    def setUp(self):
        oauth_repo_mock.reset_mock()
        client_mock.reset_mock()
        client_mock.client_id = client_id
        client_mock.client_secret = client_secret
        client_mock.user_id = user_id

    def test_query_token_with_type_hint(self):
        oauth_service._query_token(access_token, access_token, client_mock)
        oauth_repo_mock.get_token_by_access_token.assert_called_once_with(
            access_token=access_token, client_id=client_id)

        oauth_service._query_token(refresh_token, refresh_token, client_mock)
        oauth_repo_mock.get_token_by_refresh_token.assert_called_once_with(
            refresh_token=refresh_token, client_id=client_id)

    def test_query_access_token_without_type_hint(self):
        oauth_repo_mock.get_token_by_access_token.return_value = token_mock
        token = oauth_service._query_token(access_token, None, client_mock)

        oauth_repo_mock.get_token_by_access_token.assert_called_once_with(
            access_token=access_token, client_id=client_id)
        oauth_repo_mock.get_token_by_refresh_token.assert_not_called()
        self.assertEquals(token, token_mock)

    def test_query_refresh_token_without_type_hint(self):
        oauth_repo_mock.get_token_by_access_token.return_value = None
        oauth_repo_mock.get_token_by_refresh_token.return_value = token_mock

        token = oauth_service._query_token(refresh_token, None, client_mock)
        oauth_repo_mock.get_token_by_access_token.assert_called_once_with(
            access_token=refresh_token, client_id=client_id)

        oauth_repo_mock.get_token_by_refresh_token. \
            assert_called_once_with(refresh_token=refresh_token,
                                    client_id=client_id)
        self.assertEqual(token_mock, token)

    def test_get_client_by_id(self):
        expected = MagicMock(spec=dir(OAuthClient))
        expected.client_id = client_id
        oauth_repo_mock.get_client_by_id.return_value = expected

        actual = oauth_service.get_client_by_id(client_id)

        oauth_repo_mock.get_client_by_id. \
            assert_called_once_with(client_id)
        self.assertEqual(actual, expected)

    def test_create_token_with_user(self):
        request_mock = MagicMock
        request_mock.client = client_mock
        request_mock.user = None
        token = {'somekey': 'somevalue'}

        oauth_service.create_token(token, request_mock)
        oauth_repo_mock.create_token.assert_called_once_with(
            client_id=client_id, user_id=user_id, somekey='somevalue')

    def test_create_token_without_user(self):
        request_mock = MagicMock
        request_mock.client = client_mock
        token = {'somekey': 'somevalue'}

        oauth_service.create_token(token, request_mock)
        oauth_repo_mock.create_token.assert_called_once_with(
            client_id=client_id, user_id=user_id, somekey='somevalue')

    def test_get_approved_clients_by_user_id(self):
        oauth_service.get_approved_clients_by_user_id(user_id=3)
        oauth_repo_mock.get_approved_clients_by_user_id \
            .assert_called_once_with(user_id=3)

    def test_get_owned_clients_by_user_id(self):
        oauth_service.get_owned_clients_by_user_id(user_id=3)
        oauth_repo_mock.get_owned_clients_by_user_id \
            .assert_called_once_with(user_id=3)

    def test_revoke_user_tokens_by_client_id(self):
        client = MagicMock(spec=dir(OAuthClient))
        oauth_repo_mock.get_client_by_id.return_value = client

        rv = oauth_service.revoke_user_tokens_by_client_id(user_id=3,
                                                           client_id=4)
        oauth_repo_mock.revoke_user_tokens_by_client_id \
            .assert_called_once_with(user_id=3, client_id=4)
        self.assertEqual(client, rv)

    def test_revoke_user_tokens_by_client_id_no_client(self):
        oauth_repo_mock.get_client_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            oauth_service.revoke_user_tokens_by_client_id(user_id=3,
                                                          client_id=4)
        oauth_repo_mock.get_client_by_id.assert_called_once_with(client_id=4)

    def test_get_scope_descriptions(self):
        scope_dict = oauth_service.get_scope_descriptions()
        self.assertIsInstance(scope_dict, dict)
        all(self.assertIsInstance(scope, str) for scope in scope_dict.keys())
        all(self.assertIsInstance(scope, LazyString) for scope in
            scope_dict.values())

    def test_reset_client_secret(self):
        oauth_service.reset_client_secret("id")
        oauth_repo_mock.update_client_secret.assert_called_once_with(
            client_id="id", client_secret=Any(str))

    def test_reset_client_secret_no_client(self):
        oauth_repo_mock.get_client_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            oauth_service.reset_client_secret("id")

    def test_reset_client_secret_public_client(self):
        oauth_repo_mock.get_client_by_id.return_value = client_mock
        client_mock.client_secret = ''
        with self.assertRaises(BusinessRuleException):
            oauth_service.reset_client_secret("id")
