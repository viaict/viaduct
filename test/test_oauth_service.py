import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, ANY

from flask_babel import LazyString

from app import ResourceNotFoundException
from app.models.oauth.client import OAuthClient
from app.models.oauth.grant import OAuthGrant
from app.models.oauth.token import OAuthToken
from app.oauth_scopes import Scopes
from app.repository import oauth_repository as mock_spec  # rename for safety
from app.service import oauth_service
from test import Any, AnyList

oauth_repo_mock = MagicMock(spec=dir(mock_spec))

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


@patch.object(oauth_service, 'repository', oauth_repo_mock)
class TestOAuthService(unittest.TestCase):
    def setUp(self):
        oauth_repo_mock.reset_mock()

    def test_get_client_by_id(self):
        expected = MagicMock(spec=dir(OAuthClient))
        expected.client_id = client_id
        oauth_repo_mock.get_client_by_id.return_value = expected

        actual = oauth_service.get_client_by_id(client_id)

        oauth_repo_mock.get_client_by_id. \
            assert_called_once_with(client_id)
        self.assertEqual(actual, expected)

    def test_get_grant_by_client_id_and_code(self):
        expected = MagicMock(spec=dir(OAuthGrant))
        expected.client_id = client_id
        expected.code = grant_code
        oauth_repo_mock.get_grant_by_client_id_and_code \
            .return_value = expected

        actual = oauth_service.get_grant_by_client_id_and_code(
            client_id, grant_code)

        oauth_repo_mock.get_grant_by_client_id_and_code. \
            assert_called_once_with(client_id, grant_code)
        self.assertEqual(actual, expected)

    def test_create_grant(self):
        request = MagicMock()
        request.scopes = scopes_list
        request.redirect_uri = redirect_uri

        oauth_service.create_grant(client_id, code, user_id, request)

        oauth_repo_mock.create_grant.assert_called_once_with(
            client_id=client_id, code=grant_code, redirect_uri=redirect_uri,
            scopes=scopes_list, user_id=1, expires=ANY)

        expire = oauth_repo_mock.create_grant.call_args[1]['expires']
        self.assertLess(expire, datetime.utcnow() + timedelta(seconds=100))

    def test_get_token_with_access_token(self):
        expected = MagicMock(spec=dir(OAuthToken))
        oauth_repo_mock.get_token_by_access_token.return_value = expected

        actual = oauth_service.get_token(
            access_token=access_token, refresh_token=None)

        oauth_repo_mock.get_token_by_access_token \
            .assert_called_once_with(access_token)
        self.assertEqual(expected, actual)

    def test_get_token_with_refresh_token(self):
        expected = MagicMock(spec=dir(OAuthToken))
        oauth_repo_mock.get_token_by_refresh_token \
            .return_value = expected

        actual = oauth_service.get_token(
            access_token=None, refresh_token=refresh_token)

        oauth_repo_mock.get_token_by_refresh_token \
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
        oauth_repo_mock.create_token.assert_called_once_with(
            access_token, refresh_token, token_type, scopes_list,
            ANY, client_id, user_id)

        expire = oauth_repo_mock.create_token.call_args[0][4]
        self.assertLess(expire, datetime.utcnow() + timedelta(seconds=expires))

    def test_delete_grant(self):
        oauth_service.delete_grant(grant_id)
        oauth_repo_mock.delete_grant.assert_called_once_with(grant_id)

    def test_get_approved_clients_by_user_id(self):
        oauth_service.get_approved_clients_by_user_id(user_id=3)
        oauth_repo_mock.get_approved_clients_by_user_id \
            .assert_called_once_with(user_id=3)

    def test_get_owned_clients_by_user_id(self):
        oauth_service.get_owned_clients_by_user_id(user_id=3)
        oauth_repo_mock.get_owned_clients_by_user_id \
            .assert_called_once_with(user_id=3)

    def test_delete_user_tokens_by_client_id(self):
        client = MagicMock(spec=dir(OAuthClient))
        oauth_repo_mock.get_client_by_id.return_value = client

        rv = oauth_service.delete_user_tokens_by_client_id(user_id=3,
                                                           client_id=4)
        oauth_repo_mock.delete_user_tokens_by_client_id \
            .assert_called_once_with(user_id=3, client_id=4)
        self.assertEqual(client, rv)

    def test_delete_user_tokens_by_client_id_no_client(self):
        oauth_repo_mock.get_client_by_id.return_value = None

        with self.assertRaises(ResourceNotFoundException):
            oauth_service.delete_user_tokens_by_client_id(user_id=3,
                                                          client_id=4)
        oauth_repo_mock.get_client_by_id \
            .assert_called_once_with(client_id=4)

    def test_delete_token(self):
        oauth_service.delete_token(token_id=3)
        oauth_repo_mock.delete_token.assert_called_once_with(token_id=3)

    def test_get_scope_descriptions(self):
        scope_dict = oauth_service.get_scope_descriptions()
        self.assertIsInstance(scope_dict, dict)
        all(self.assertIsInstance(scope, str) for scope in scope_dict.keys())
        all(self.assertIsInstance(scope, LazyString) for scope in
            scope_dict.values())

    def test_generate_random_str(self):
        generated = oauth_service.generate_random_str(20)
        self.assertTrue(len(generated) == 20)
        generated = oauth_service.generate_random_str(28)
        self.assertTrue(len(generated) == 28)

    def test_generate_client_id(self):
        oauth_repo_mock.get_client_by_id.return_value = None
        oauth_service.generate_client_id()

        oauth_repo_mock.get_client_by_id.assert_called_once_with(
            client_id=Any(str))

    def test_generate_client_id_duplicate_found(self):
        # Set a iterator for the return value.
        oauth_repo_mock.get_client_by_id.side_effect = ["id", None]
        oauth_service.generate_client_id()
        self.assertEqual(oauth_repo_mock.get_client_by_id.call_count, 2)

        # Apparently the side effects are not canceled by reset mock?
        oauth_repo_mock.get_client_by_id.side_effect = None

    def test_generate_client_secret(self):
        oauth_repo_mock.get_client_by_secret.return_value = None
        oauth_service.generate_client_secret()

        oauth_repo_mock.get_client_by_secret.assert_called_once_with(
            client_secret=Any(str))

    def test_generate_client_secret_duplicate_found(self):
        # Set a iterator for the return value.
        oauth_repo_mock.get_client_by_secret.side_effect = \
            ["secret", None]
        oauth_service.generate_client_secret()
        self.assertEqual(oauth_repo_mock.get_client_by_secret.call_count,
                         2)
        # Apparently the side effects are not canceled by reset mock?
        oauth_repo_mock.get_client_by_secret.side_effect = None

    def test_create_client(self):
        oauth_repo_mock.get_client_by_id.return_value = None
        oauth_repo_mock.get_client_by_secret.return_value = None

        scopes = [Scopes.pimpy_read, Scopes.pimpy_write]

        oauth_service.create_client(user_id=42, name="name",
                                    description="desc",
                                    redirect_uri_list=redirect_uri,
                                    scopes=scopes)

        oauth_repo_mock.create_client.assert_called_once_with(
            client_id=Any(str), client_secret=Any(str), name="name",
            description="desc", redirect_uris=[redirect_uri], user_id=42,
            confidential=False, default_scopes=AnyList(str))

    def test_reset_client_secret(self):
        oauth_repo_mock.get_client_by_id.return_value = None
        oauth_service.reset_client_secret("id")

        oauth_repo_mock.update_client_secret.assert_called_once_with(
            client_id="id", client_secret=Any(str))

    def test_split_redirect_uris(self):
        uri_str, uri_list = "a", ["a"]
        self.assertEqual(oauth_service.split_redirect_uris(uri_str),
                         uri_list)

        uri_str, uri_list = "a,b", ["a", "b"]
        self.assertEqual(oauth_service.split_redirect_uris(uri_str),
                         uri_list)

        uri_str, uri_list = "a, b", ["a", "b"]
        self.assertEqual(oauth_service.split_redirect_uris(uri_str),
                         uri_list)

        uri_str, uri_list = "a, b,", ["a", "b"]
        self.assertEqual(oauth_service.split_redirect_uris(uri_str),
                         uri_list)

    def test_update_client_details(self):
        uris = "uri, uri2"
        new_scopes = [Scopes.pimpy_write]

        oauth_service.update_client(
            client_id="id", name="name", description="desc",
            redirect_uri_list=uris, scopes=new_scopes)
        oauth_repo_mock.update_client_details.assert_called_once_with(
            client_id="id", name="name", description="desc")

        # Assert retrieving old scopes and redirect uris
        oauth_repo_mock.get_redirect_uris_by_client_id \
            .assert_called_once_with(client_id="id")
        oauth_repo_mock.get_scopes_by_client_id \
            .assert_called_once_with(client_id="id")

    def test_update_client_removed_uri(self):
        uris = ["uri", "uri2"]
        new_uris = "uri"

        new_scopes = [Scopes.pimpy_write]

        oauth_repo_mock.get_redirect_uris_by_client_id.return_value = uris
        oauth_service.update_client(client_id="", name="", description="",
                                    redirect_uri_list=new_uris,
                                    scopes=new_scopes)

        oauth_repo_mock.delete_redirect_uris.assert_called_once_with(
            client_id=Any(str), redirect_uri_list={"uri2"})
        self.assertEqual(oauth_repo_mock.insert_redirect_uris.call_count, 0)

    def test_update_client_added_uri(self):
        uris = ["uri"]
        new_uris = "uri, uri2"

        new_scopes = [Scopes.pimpy_write]

        oauth_repo_mock.get_redirect_uris_by_client_id.return_value = uris
        oauth_service.update_client(client_id="", name="", description="",
                                    redirect_uri_list=new_uris,
                                    scopes=new_scopes)

        self.assertEqual(oauth_repo_mock.delete_redirect_uris.call_count, 0)
        oauth_repo_mock.insert_redirect_uris.assert_called_once_with(
            client_id=Any(str), redirect_uri_list={"uri2"})

    def test_update_client_removed_scopes(self):
        old_scopes = [Scopes.pimpy_read]
        new_scopes = [Scopes.pimpy_read, Scopes.pimpy_write]

        oauth_repo_mock.get_scopes_by_client_id.return_value = old_scopes

        oauth_service.update_client(client_id="", name="", description="",
                                    redirect_uri_list=redirect_uri,
                                    scopes=new_scopes)

        oauth_repo_mock.insert_scopes.assert_called_once_with(
            client_id=Any(str), scopes_list={Scopes.pimpy_write})
        self.assertEqual(oauth_repo_mock.delete_scopes.call_count, 0)

    def test_update_client_added_scopes(self):
        old_scopes = [Scopes.pimpy_read, Scopes.pimpy_write]
        new_scopes = [Scopes.pimpy_write]

        oauth_repo_mock.get_scopes_by_client_id.return_value = old_scopes

        oauth_service.update_client(client_id="", name="", description="",
                                    redirect_uri_list=redirect_uri,
                                    scopes=new_scopes)

        oauth_repo_mock.delete_scopes.assert_called_once_with(
            client_id=Any(str), scopes_list={Scopes.pimpy_read})
        self.assertEqual(oauth_repo_mock.insert_scopes.call_count, 0)
