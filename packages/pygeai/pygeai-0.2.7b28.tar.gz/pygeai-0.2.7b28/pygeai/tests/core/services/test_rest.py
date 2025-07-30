import unittest
from unittest.mock import patch, Mock

from pygeai.core.services.rest import ApiService


class TestApiService(unittest.TestCase):
    """
    python -m unittest pygeai.tests.test_services.TestApiService
    """
    def setUp(self):
        self.base_url = "https://api.example.com"
        self.api_service = ApiService(self.base_url, username="user", password="pass", token="test_token")

    def test_init_with_credentials(self):
        service = ApiService(self.base_url, username="user", password="pass", token="token")

        self.assertEqual(service.base_url, self.base_url)
        self.assertEqual(service.username, "user")
        self.assertEqual(service.password, "pass")
        self.assertEqual(service.token, "token")

    def test_init_without_credentials(self):
        service = ApiService(self.base_url)

        self.assertEqual(service.base_url, self.base_url)
        self.assertIsNone(service.username)
        self.assertIsNone(service.password)
        self.assertIsNone(service.token)

    @patch('requests.Session.get')
    def test_get_request_with_basic_auth(self, mock_get):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_get.return_value = mock_response

        response = self.api_service.get(endpoint="test_endpoint", params={"key": "value"}, headers={"Custom": "Header"})

        mock_get.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            params={"key": "value"},
            headers={"Custom": "Header"}
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.get')
    def test_get_request_with_token(self, mock_get):
        api_service = ApiService(self.base_url, token="test_token")
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_get.return_value = mock_response

        response = api_service.get(endpoint="test_endpoint", headers={"Custom": "Header"})

        mock_get.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            params=None,
            headers={"Custom": "Header", "Authorization": "Bearer test_token"}
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.post')
    def test_post_request_json(self, mock_post):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_post.return_value = mock_response

        response = self.api_service.post(endpoint="test_endpoint", data={"key": "value"}, headers={"Custom": "Header"})

        mock_post.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            json={"key": "value"},
            headers={"Custom": "Header"}
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.post')
    def test_post_request_form(self, mock_post):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_post.return_value = mock_response

        response = self.api_service.post(endpoint="test_endpoint", data={"key": "value"}, headers={"Custom": "Header"}, form=True)

        mock_post.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            data={"key": "value"},
            headers={"Custom": "Header"}
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.post')
    def test_stream_post_request(self, mock_post):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_response.iter_lines.return_value = ["line1", "line2"]
        mock_post.return_value = mock_response

        result = list(self.api_service.stream_post(endpoint="test_endpoint", data={"key": "value"}))

        mock_post.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            json={"key": "value"},
            headers=None,
            stream=True
        )
        self.assertEqual(result, ["line1", "line2"])

    @patch('requests.Session.post')
    def test_post_file_binary(self, mock_post):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_post.return_value = mock_response
        mock_file = Mock()

        response = self.api_service.post_file_binary(endpoint="test_endpoint", file=mock_file)

        mock_post.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            headers=None,
            data=mock_file
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.post')
    def test_post_files_multipart(self, mock_post):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_post.return_value = mock_response
        mock_files = {"file": "path/to/file"}

        response = self.api_service.post_files_multipart(endpoint="test_endpoint", data={"key": "value"}, files=mock_files)

        mock_post.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            headers=None,
            data={"key": "value"},
            files=mock_files
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.put')
    def test_put_request(self, mock_put):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_put.return_value = mock_response

        response = self.api_service.put(endpoint="test_endpoint", data={"key": "value"}, headers={"Custom": "Header"})

        mock_put.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            json={"key": "value"},
            headers={"Custom": "Header", "Content-Type": "application/json"}
        )
        self.assertEqual(response, mock_response)

    @patch('requests.Session.delete')
    def test_delete_request(self, mock_delete):
        mock_response = Mock()
        mock_response.url = f"{self.base_url}/test_endpoint"
        mock_delete.return_value = mock_response

        response = self.api_service.delete(endpoint="test_endpoint", data={"key": "value"}, headers={"Custom": "Header"})

        mock_delete.assert_called_once_with(
            url=f"{self.base_url}/test_endpoint",
            headers={"Custom": "Header"},
            params={"key": "value"}
        )
        self.assertEqual(response, mock_response)

    def test_add_endpoint_to_url_with_protocol(self):
        result = self.api_service._add_endpoint_to_url("test_endpoint")

        self.assertEqual(result, f"{self.base_url}/test_endpoint")

    def test_add_endpoint_to_url_without_protocol(self):
        api_service = ApiService("api.example.com")
        result = api_service._add_endpoint_to_url("test_endpoint")

        self.assertEqual(result, "https://api.example.com/test_endpoint")

    def test_add_token_to_headers_new_headers(self):
        result = self.api_service._add_token_to_headers()

        self.assertEqual(result, {"Authorization": "Bearer test_token"})

    def test_add_token_to_headers_existing_headers(self):
        headers = {"Custom": "Header"}
        result = self.api_service._add_token_to_headers(headers)

        self.assertEqual(result, {"Custom": "Header", "Authorization": "Bearer test_token"})

