import unittest
from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import patch

from pygeai.organization.clients import OrganizationClient
from pygeai.core.base.session import get_session
from pygeai.organization.endpoints import GET_ASSISTANT_LIST_V1, GET_PROJECT_LIST_V1, GET_PROJECT_V1, CREATE_PROJECT_V1, \
    UPDATE_PROJECT_V1, DELETE_PROJECT_V1, GET_PROJECT_TOKENS_V1, GET_REQUEST_DATA_V1

session = get_session()


class TestOrganizationClient(TestCase):
    """
    python -m unittest pygeai.tests.organization.test_clients.TestOrganizationClient
    """

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_assistant_list(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"assistants": [{"name": "assistant1"}, {"name": "assistant2"}]}

        client = OrganizationClient()
        result = client.get_assistant_list()

        self.assertIsNotNone(result)
        self.assertEqual(len(result['assistants']), 2)
        self.assertEqual(result['assistants'][0]['name'], "assistant1")
        self.assertEqual(result['assistants'][1]['name'], "assistant2")

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_list(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"projects": [{"name": "project1"}, {"name": "project2"}]}

        client = OrganizationClient()
        result = client.get_project_list()

        self.assertIsNotNone(result)
        self.assertEqual(len(result['projects']), 2)
        self.assertEqual(result['projects'][0]['name'], "project1")
        self.assertEqual(result['projects'][1]['name'], "project2")

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_data(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"project": {"id": "123", "name": "project1"}}

        client = OrganizationClient()
        result = client.get_project_data("123")

        self.assertIsNotNone(result)
        self.assertEqual(result['project']['name'], "project1")

    @patch("pygeai.core.services.rest.ApiService.post")
    def test_create_project(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"project": {"id": "123", "name": "project1"}}

        client = OrganizationClient()
        result = client.create_project("project1", "admin@example.com", "A test project")

        self.assertIsNotNone(result)
        self.assertEqual(result['project']['name'], "project1")

    @patch("pygeai.core.services.rest.ApiService.put")
    def test_update_project(self, mock_put):
        mock_response = mock_put.return_value
        mock_response.json.return_value = {"project": {"id": "123", "name": "updated_project"}}

        client = OrganizationClient()
        result = client.update_project("123", "updated_project", "Updated description")

        self.assertIsNotNone(result)
        self.assertEqual(result['project']['name'], "updated_project")

    @patch("pygeai.core.services.rest.ApiService.delete")
    def test_delete_project(self, mock_delete):
        mock_response = mock_delete.return_value
        mock_response.json.return_value = {"status": "deleted"}

        client = OrganizationClient()
        result = client.delete_project("123")

        self.assertIsNotNone(result)
        self.assertEqual(result['status'], "deleted")

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_tokens(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"tokens": ["token1", "token2"]}

        client = OrganizationClient()
        result = client.get_project_tokens("123")

        self.assertIsNotNone(result)
        self.assertEqual(len(result['tokens']), 2)
        self.assertEqual(result['tokens'][0], "token1")
        self.assertEqual(result['tokens'][1], "token2")

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_export_request_data(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"requests": [{"id": "1", "status": "pending"}]}

        client = OrganizationClient()
        result = client.export_request_data()

        self.assertIsNotNone(result)
        self.assertEqual(len(result['requests']), 1)
        self.assertEqual(result['requests'][0]['status'], "pending")

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_assistant_list_json_decode_error(self, mock_get):
        """Test handling JSON decode error in get_assistant_list"""
        mock_response = mock_get.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.get_assistant_list(detail="full")

        self.assertEqual(result, "Invalid JSON response")
        mock_get.assert_called_once_with(endpoint=GET_ASSISTANT_LIST_V1, params={"detail": "full"})

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_list_with_name(self, mock_get):
        """Test get_project_list with detail and name parameters"""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"projects": [{"name": "specific_project"}]}

        client = OrganizationClient()
        result = client.get_project_list(detail="full", name="specific_project")

        self.assertIsNotNone(result)
        self.assertEqual(len(result['projects']), 1)
        self.assertEqual(result['projects'][0]['name'], "specific_project")
        mock_get.assert_called_once_with(
            endpoint=GET_PROJECT_LIST_V1,
            params={"detail": "full", "name": "specific_project"}
        )

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_list_json_decode_error(self, mock_get):
        """Test handling JSON decode error in get_project_list"""
        mock_response = mock_get.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.get_project_list(detail="full", name="test_project")

        self.assertEqual(result, "Invalid JSON response")
        mock_get.assert_called_once_with(
            endpoint=GET_PROJECT_LIST_V1,
            params={"detail": "full", "name": "test_project"}
        )

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_data_json_decode_error(self, mock_get):
        """Test handling JSON decode error in get_project_data"""
        mock_response = mock_get.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.get_project_data("123")

        self.assertEqual(result, "Invalid JSON response")
        mock_get.assert_called_once_with(endpoint=GET_PROJECT_V1.format(id="123"))

    @patch("pygeai.core.services.rest.ApiService.post")
    def test_create_project_with_usage_limit(self, mock_post):
        """Test create_project with usage_limit parameter"""
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"project": {"id": "123", "name": "project1"}}

        client = OrganizationClient()
        usage_limit = {"type": "Requests", "threshold": 1000}
        result = client.create_project("project1", "admin@example.com", "A test project", usage_limit)

        self.assertIsNotNone(result)
        self.assertEqual(result['project']['name'], "project1")
        mock_post.assert_called_once_with(
            endpoint=CREATE_PROJECT_V1,
            data={
                "name": "project1",
                "administratorUserEmail": "admin@example.com",
                "description": "A test project",
                "usageLimit": usage_limit
            }
        )

    @patch("pygeai.core.services.rest.ApiService.post")
    def test_create_project_json_decode_error(self, mock_post):
        """Test handling JSON decode error in create_project"""
        mock_response = mock_post.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.create_project("project1", "admin@example.com")

        self.assertEqual(result, "Invalid JSON response")
        mock_post.assert_called_once_with(
            endpoint=CREATE_PROJECT_V1,
            data={"name": "project1", "administratorUserEmail": "admin@example.com", "description": None}
        )

    @patch("pygeai.core.services.rest.ApiService.put")
    def test_update_project_json_decode_error(self, mock_put):
        """Test handling JSON decode error in update_project"""
        mock_response = mock_put.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.update_project("123", "updated_project")

        self.assertEqual(result, "Invalid JSON response")
        mock_put.assert_called_once_with(
            endpoint=UPDATE_PROJECT_V1.format(id="123"),
            data={"name": "updated_project", "description": None}
        )

    @patch("pygeai.core.services.rest.ApiService.delete")
    def test_delete_project_json_decode_error(self, mock_delete):
        """Test handling JSON decode error in delete_project"""
        mock_response = mock_delete.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.delete_project("123")

        self.assertEqual(result, "Invalid JSON response")
        mock_delete.assert_called_once_with(endpoint=DELETE_PROJECT_V1.format(id="123"))

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_get_project_tokens_json_decode_error(self, mock_get):
        """Test handling JSON decode error in get_project_tokens"""
        mock_response = mock_get.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.get_project_tokens("123")

        self.assertEqual(result, "Invalid JSON response")
        mock_get.assert_called_once_with(endpoint=GET_PROJECT_TOKENS_V1.format(id="123"))

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_export_request_data_with_params(self, mock_get):
        """Test export_request_data with all parameters"""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"requests": [{"id": "1", "status": "completed"}]}

        client = OrganizationClient()
        result = client.export_request_data(assistant_name="assistant1", status="completed", skip=10, count=5)

        self.assertIsNotNone(result)
        self.assertEqual(len(result['requests']), 1)
        self.assertEqual(result['requests'][0]['status'], "completed")
        mock_get.assert_called_once_with(
            endpoint=GET_REQUEST_DATA_V1,
            params={"assistantName": "assistant1", "status": "completed", "skip": 10, "count": 5}
        )

    @patch("pygeai.core.services.rest.ApiService.get")
    def test_export_request_data_json_decode_error(self, mock_get):
        """Test handling JSON decode error in export_request_data"""
        mock_response = mock_get.return_value
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"

        client = OrganizationClient()
        result = client.export_request_data(assistant_name="assistant1")

        self.assertEqual(result, "Invalid JSON response")
        mock_get.assert_called_once_with(
            endpoint=GET_REQUEST_DATA_V1,
            params={"assistantName": "assistant1", "status": None, "skip": 0, "count": 0}
        )