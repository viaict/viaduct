import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY

from app.models.oauth.client import OAuthClient
from app.models.oauth.grant import OAuthGrant
from app.models.oauth.token import OAuthToken
from app.repository import oauth_repository
from app.service import oauth_service

oauth_repository_mock = MagicMock(spec=dir(oauth_repository))

access_token = "access_token"
refresh_token = "refresh_token"
client_id = "client_id"
grant_code = "grant_code"
code = {"code": "grant_code"}
scopes = "SCOPE1 SCOPE2 SCOPE3"
scopes_list = ["SCOPE1", "SCOPE2", "SCOPE3"]
redirect_uri = "http://svia.nl"
token_type = "Bearer"
expires = 3600
user_id = 1
grant_id = 2


@patch.object(oauth_service, 'oauth_repository', oauth_repository_mock)
class TestOAuthService(unittest.TestCase):
    def setUp(self):
        oauth_repository_mock.reset_mock()

    def test_get_client_by_id(self):
        expected = MagicMock(spec=dir(OAuthClient))
        expected.client_id = client_id
        oauth_repository_mock.get_client_by_id.return_value = expected

        actual = oauth_service.get_client_by_id(client_id)

        oauth_repository_mock.get_client_by_id. \
            assert_called_once_with(client_id)
        self.assertEqual(actual, expected)

    def test_get_grant_by_client_id_and_code(self):
        expected = MagicMock(spec=dir(OAuthGrant))
        expected.client_id = client_id
        expected.code = grant_code
        oauth_repository_mock.get_grant_by_client_id_and_code \
            .return_value = expected

        actual = oauth_service.get_grant_by_client_id_and_code(
            client_id, grant_code)

        oauth_repository_mock.get_grant_by_client_id_and_code. \
            assert_called_once_with(client_id, grant_code)
        self.assertEqual(actual, expected)

    def test_create_grant(self):
        request = MagicMock()
        request.scopes = scopes_list
        request.redirect_uri = redirect_uri

        oauth_service.create_grant(client_id, code, user_id, request)

        oauth_repository_mock.create_grant.assert_called_once_with(
            client_id=client_id, code=grant_code, redirect_uri=redirect_uri,
            scopes=scopes_list, user_id=1, expires=ANY)

        expire = oauth_repository_mock.create_grant.call_args[1]['expires']
        self.assertLess(expire, datetime.utcnow() + timedelta(seconds=100))

    def test_get_token_with_access_token(self):
        expected = MagicMock(spec=dir(OAuthToken))
        oauth_repository_mock.get_token_by_access_token.return_value = expected

        actual = oauth_service.get_token(
            access_token=access_token, refresh_token=None)

        oauth_repository_mock.get_token_by_access_token \
            .assert_called_once_with(access_token)
        self.assertEqual(expected, actual)

    def test_get_token_with_refresh_token(self):
        expected = MagicMock(spec=dir(OAuthToken))
        oauth_repository_mock.get_token_by_refresh_token \
            .return_value = expected

        actual = oauth_service.get_token(
            access_token=None, refresh_token=refresh_token)

        oauth_repository_mock.get_token_by_refresh_token \
            .assert_called_once_with(refresh_token)
        self.assertEqual(expected, actual)

    def test_get_token_without_token(self):
        rv = oauth_service.get_token(access_token=None, refresh_token=None)
        self.assertIsNone(rv)

    def test_create_token(self):
        token = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "scope": scopes,
            "token_type": token_type,
            "expires_in": 3600
        }

        request = MagicMock()
        request.client.client_id = client_id

        oauth_service.create_token(token, user_id, request)
        oauth_repository_mock.create_token.assert_called_once_with(
            access_token, refresh_token, token_type, scopes_list,
            ANY, client_id, user_id)

        expire = oauth_repository_mock.create_token.call_args[0][4]
        self.assertLess(expire, datetime.utcnow() + timedelta(seconds=expires))

    def test_delete_grant(self):
        oauth_service.delete_grant(grant_id)
        oauth_repository_mock.delete_grant.assert_called_once_with(grant_id)
