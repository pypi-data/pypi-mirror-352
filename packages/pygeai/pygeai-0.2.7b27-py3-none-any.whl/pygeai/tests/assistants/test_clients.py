import unittest
from unittest.mock import patch, MagicMock
from json import JSONDecodeError

from pygeai.assistant.clients import AssistantClient


class TestAssistantClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.assistants.test_clients.TestAssistantClient
    """
    def setUp(self):
        # Mock the BaseClient __init__ to bypass API_KEY and BASE_URL checks
        with patch('pygeai.core.base.clients.BaseClient.__init__', return_value=None):
            self.client = AssistantClient()
        self.mock_response = MagicMock()
        self.client.api_service = MagicMock()

    def test_get_assistant_data_successful_json_response(self):
        assistant_id = "test_id"
        detail = "summary"
        expected_response = {"id": assistant_id, "name": "Test Assistant"}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_assistant_data(assistant_id, detail)

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_get_assistant_data_json_decode_error(self):
        assistant_id = "test_id"
        detail = "full"
        expected_text = "Invalid JSON response"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_assistant_data(assistant_id, detail)

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, expected_text)

    def test_create_assistant_successful_json_response(self):
        assistant_type = "text"
        name = "New Assistant"
        prompt = "Help with text"
        expected_response = {"id": "new_id", "name": name}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_assistant(assistant_type, name, prompt)

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_create_assistant_json_decode_error(self):
        assistant_type = "chat"
        name = "Chat Assistant"
        prompt = "Chat prompt"
        expected_text = "Error in response"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_assistant(assistant_type, name, prompt)

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, expected_text)

    def test_update_assistant_successful_json_response(self):
        assistant_id = "test_id"
        status = 1
        action = "save"
        expected_response = {"id": assistant_id, "status": status}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_assistant(assistant_id, status, action)

        self.client.api_service.put.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_update_assistant_json_decode_error(self):
        assistant_id = "test_id"
        status = 2
        action = "saveNewRevision"
        expected_text = "Update failed"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_assistant(assistant_id, status, action)

        self.client.api_service.put.assert_called_once()
        self.assertEqual(result, expected_text)

    def test_delete_assistant_successful_json_response(self):
        assistant_id = "test_id"
        expected_response = {"message": "Assistant deleted"}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.delete.return_value = self.mock_response

        result = self.client.delete_assistant(assistant_id)

        self.client.api_service.delete.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_delete_assistant_json_decode_error(self):
        assistant_id = "test_id"
        expected_text = "Delete error"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.delete.return_value = self.mock_response

        result = self.client.delete_assistant(assistant_id)

        self.client.api_service.delete.assert_called_once()
        self.assertEqual(result, expected_text)

    def test_send_chat_request_successful_json_response(self):
        assistant_name = "Test Assistant"
        messages = [{"role": "user", "content": "Hello"}]
        expected_response = {"response": "Hi there!"}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.send_chat_request(assistant_name, messages)

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_send_chat_request_json_decode_error(self):
        assistant_name = "Test Assistant"
        messages = [{"role": "user", "content": "Hello"}]
        expected_text = "Chat error"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.send_chat_request(assistant_name, messages)

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, expected_text)

    def test_get_request_status_successful_json_response(self):
        request_id = "req_123"
        expected_response = {"status": "completed"}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_request_status(request_id)

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_get_request_status_json_decode_error(self):
        request_id = "req_123"
        expected_text = "Status error"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_request_status(request_id)

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, expected_text)

    def test_cancel_request_successful_json_response(self):
        request_id = "req_123"
        expected_response = {"message": "Request cancelled"}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.cancel_request(request_id)

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, expected_response)

    def test_cancel_request_json_decode_error(self):
        request_id = "req_123"
        expected_text = "Cancel error"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = expected_text
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.cancel_request(request_id)

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, expected_text)

if __name__ == '__main__':
    unittest.main()