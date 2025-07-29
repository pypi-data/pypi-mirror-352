import unittest
from unittest.mock import MagicMock
from json import JSONDecodeError
from pygeai.gam.clients import GAMClient


class TestGAMClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.gam.test_clients.TestGAMClient
    """

    def setUp(self):
        self.client = GAMClient()
        self.client.api_service = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"status": "success"}
        self.mock_response.text = "success text"

    def test_get_access_token_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.get_access_token(
            client_id="test-client-id",
            client_secret="test-client-secret",
            grant_type="password",
            authentication_type_name="local",
            scope="gam_user_data",
            username="test-user",
            password="test-pass",
            initial_properties={"Company": "GeneXus"},
            repository="test-repo",
            request_token_type="OAuth"
        )

        self.client.api_service.post.assert_called_once()
        data = self.client.api_service.post.call_args[1]['data']
        self.assertEqual(data['client_id'], "test-client-id")
        self.assertEqual(data['client_secret'], "test-client-secret")
        self.assertEqual(data['grant_type'], "password")
        self.assertEqual(data['authentication_type_name'], "local")
        self.assertEqual(data['scope'], "gam_user_data")
        self.assertEqual(data['username'], "test-user")
        self.assertEqual(data['password'], "test-pass")
        self.assertEqual(data['initial_properties'], {"Company": "GeneXus"})
        self.assertEqual(data['repository'], "test-repo")
        self.assertEqual(data['request_token_type'], "OAuth")
        headers = self.client.api_service.post.call_args[1]['headers']
        self.assertEqual(headers['Content-Type'], "application/x-www-form-urlencoded")
        self.assertTrue(self.client.api_service.post.call_args[1]['form'])
        self.assertEqual(result, {"status": "success"})

    def test_get_access_token_minimal_data(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.get_access_token(
            client_id="test-client-id",
            client_secret="test-client-secret",
            username="test-user",
            password="test-pass"
        )

        self.client.api_service.post.assert_called_once()
        data = self.client.api_service.post.call_args[1]['data']
        self.assertEqual(data['client_id'], "test-client-id")
        self.assertEqual(data['client_secret'], "test-client-secret")
        self.assertEqual(data['username'], "test-user")
        self.assertEqual(data['password'], "test-pass")
        self.assertEqual(result, {"status": "success"})

    def test_get_access_token_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.get_access_token(
            client_id="test-client-id",
            client_secret="test-client-secret",
            username="test-user",
            password="test-pass"
        )

        self.assertEqual(result, "success text")
        self.client.api_service.post.assert_called_once()

    def test_get_user_info_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_user_info(
            access_token="test-access-token"
        )

        self.client.api_service.get.assert_called_once()
        headers = self.client.api_service.get.call_args[1]['headers']
        self.assertEqual(headers['Authorization'], "test-access-token")
        self.assertEqual(headers['Content-Type'], "application/x-www-form-urlencoded")
        self.assertEqual(result, {"status": "success"})

    def test_get_user_info_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_user_info(
            access_token="test-access-token"
        )

        self.assertEqual(result, "success text")
        self.client.api_service.get.assert_called_once()

    def test_refresh_access_token_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.refresh_access_token(
            client_id="test-client-id",
            client_secret="test-client-secret",
            grant_type="refresh_token",
            refresh_token="test-refresh-token"
        )

        self.client.api_service.post.assert_called_once()
        data = self.client.api_service.post.call_args[1]['data']
        self.assertEqual(data['client_id'], "test-client-id")
        self.assertEqual(data['client_secret'], "test-client-secret")
        self.assertEqual(data['grant_type'], "refresh_token")
        self.assertEqual(data['refresh_token'], "test-refresh-token")
        headers = self.client.api_service.post.call_args[1]['headers']
        self.assertEqual(headers['Content-Type'], "application/x-www-form-urlencoded")
        self.assertTrue(self.client.api_service.post.call_args[1]['form'])
        self.assertEqual(result, {"status": "success"})

    def test_refresh_access_token_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.refresh_access_token(
            client_id="test-client-id",
            client_secret="test-client-secret",
            refresh_token="test-refresh-token"
        )

        self.assertEqual(result, "success text")
        self.client.api_service.post.assert_called_once()

    def test_get_authentication_types_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_authentication_types()

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_get_authentication_types_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_authentication_types()

        self.assertEqual(result, "success text")
        self.client.api_service.get.assert_called_once()

