import unittest
from unittest.mock import MagicMock
from json import JSONDecodeError
from pygeai.core.llm.clients import LlmClient


class TestLlmClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.core.llm.test_clients.TestLlmClient
    """

    def setUp(self):
        self.client = LlmClient()
        self.client.api_service = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"status": "success"}
        self.mock_response.text = "error text"

    def test_get_provider_list_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_provider_list()

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_get_provider_list_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_provider_list()

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, "error text")

    def test_get_provider_data_success(self):
        provider_name = "test-provider"
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_provider_data(provider_name=provider_name)

        self.client.api_service.get.assert_called_once()
        endpoint = self.client.api_service.get.call_args[1]['endpoint']
        self.assertIn(provider_name, endpoint)
        self.assertEqual(result, {"status": "success"})

    def test_get_provider_data_json_decode_error(self):
        provider_name = "test-provider"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_provider_data(provider_name=provider_name)

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, "error text")

    def test_get_provider_models_success(self):
        provider_name = "test-provider"
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_provider_models(provider_name=provider_name)

        self.client.api_service.get.assert_called_once()
        endpoint = self.client.api_service.get.call_args[1]['endpoint']
        self.assertIn(provider_name, endpoint)
        self.assertEqual(result, {"status": "success"})

    def test_get_provider_models_json_decode_error(self):
        provider_name = "test-provider"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_provider_models(provider_name=provider_name)

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, "error text")

    def test_get_model_data_with_model_name(self):
        provider_name = "test-provider"
        model_name = "test-model"
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_model_data(
            provider_name=provider_name,
            model_name=model_name
        )

        self.client.api_service.get.assert_called_once()
        endpoint = self.client.api_service.get.call_args[1]['endpoint']
        self.assertIn(provider_name, endpoint)
        self.assertIn(model_name, endpoint)
        self.assertEqual(result, {"status": "success"})

    def test_get_model_data_with_model_id(self):
        provider_name = "test-provider"
        model_id = "test-model-id"
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_model_data(
            provider_name=provider_name,
            model_id=model_id
        )

        self.client.api_service.get.assert_called_once()
        endpoint = self.client.api_service.get.call_args[1]['endpoint']
        self.assertIn(provider_name, endpoint)
        self.assertIn(model_id, endpoint)
        self.assertEqual(result, {"status": "success"})

    def test_get_model_data_json_decode_error(self):
        provider_name = "test-provider"
        model_name = "test-model"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_model_data(
            provider_name=provider_name,
            model_name=model_name
        )

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, "error text")

