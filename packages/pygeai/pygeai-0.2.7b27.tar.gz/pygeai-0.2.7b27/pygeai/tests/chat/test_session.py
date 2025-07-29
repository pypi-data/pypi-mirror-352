import unittest
from unittest.mock import patch, MagicMock
from pygeai.chat.session import AgentChatSession


class TestAgentChatSession(unittest.TestCase):
    """
    python -m unittest pygeai.tests.chat.test_session.TestAgentChatSession
    """
    def setUp(self):
        self.agent_name = "test_agent"
        self.session = AgentChatSession(agent_name=self.agent_name)
        self.mock_client = MagicMock()
        self.session.client = self.mock_client
        self.messages = [{"role": "user", "content": "Hello"}]
        self.llm_settings = {
            "temperature": 0.6,
            "max_tokens": 800,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.2
        }

    def test_init_sets_agent_name_and_client(self):
        self.assertEqual(self.session.agent_name, self.agent_name)
        self.assertIsNotNone(self.session.client)

    def test_stream_answer_calls_chat_completion_with_stream_true(self):
        expected_response = {"stream": "data"}
        self.mock_client.chat_completion.return_value = expected_response

        result = self.session.stream_answer(self.messages)

        self.mock_client.chat_completion.assert_called_once_with(
            model=f"saia:agent:{self.agent_name}",
            messages=self.messages,
            stream=True,
            **self.llm_settings
        )
        self.assertEqual(result, expected_response)

    def test_get_answer_calls_chat_completion_with_stream_false(self):
        expected_content = "Hi there!"
        expected_response = {"choices": [{"message": {"content": expected_content}}]}
        self.mock_client.chat_completion.return_value = expected_response

        result = self.session.get_answer(self.messages)

        self.mock_client.chat_completion.assert_called_once_with(
            model=f"saia:agent:{self.agent_name}",
            messages=self.messages,
            stream=False,
            **self.llm_settings
        )
        self.assertEqual(result, expected_content)

    def test_get_answer_handles_exception_and_returns_empty_string(self):
        self.mock_client.chat_completion.side_effect = Exception("API error")

        with patch('pygeai.logger.error') as mock_logger:
            result = self.session.get_answer(self.messages)

        self.mock_client.chat_completion.assert_called_once_with(
            model=f"saia:agent:{self.agent_name}",
            messages=self.messages,
            stream=False,
            **self.llm_settings
        )
        mock_logger.assert_called_once_with(f"Unable to communicate with specified agent {self.agent_name}: API error")
        self.assertEqual(result, "")
