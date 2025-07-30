import unittest
from unittest.mock import MagicMock
from json import JSONDecodeError
from pygeai.lab.agents.clients import AgentClient


class TestAgentClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.lab.agents.test_clients.TestAgentClient
    """

    def setUp(self):
        self.client = AgentClient()
        self.client.api_service = MagicMock()
        self.project_id = "test-project-id"
        self.agent_id = "test-agent-id"
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"status": "success"}
        self.mock_response.text = "success text"

    def test_list_agents_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.list_agents(
            project_id=self.project_id,
            status="active",
            start=0,
            count=10,
            access_scope="private",
            allow_drafts=True,
            allow_external=True
        )

        self.client.api_service.get.assert_called_once()
        params = self.client.api_service.get.call_args[1]['params']
        self.assertEqual(params['status'], "active")
        self.assertEqual(params['start'], 0)
        self.assertEqual(params['count'], 10)
        self.assertEqual(params['accessScope'], "private")
        self.assertTrue(params['allowDrafts'])
        self.assertTrue(params['allowExternal'])
        headers = self.client.api_service.get.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_list_agents_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.list_agents(
            project_id=self.project_id
        )

        self.assertEqual(result, "success text")
        self.client.api_service.get.assert_called_once()

    def test_create_agent_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_agent(
            project_id=self.project_id,
            name="Test Agent",
            access_scope="private",
            public_name="test-agent",
            job_description="Agent Role",
            avatar_image="http://example.com/avatar.png",
            description="Agent Description",
            agent_data_prompt={"instructions": "Do this task"},
            agent_data_llm_config={"maxTokens": 100, "timeout": 30},
            agent_data_models=[{"name": "gpt-4o"}],
            agent_data_resource_pools=[{"name": "pool1", "tools": [{"name": "tool1"}]}],
            automatic_publish=True
        )

        self.client.api_service.post.assert_called_once()
        data = self.client.api_service.post.call_args[1]['data']['agentDefinition']
        self.assertEqual(data['name'], "Test Agent")
        self.assertEqual(data['accessScope'], "private")
        self.assertEqual(data['publicName'], "test-agent")
        self.assertEqual(data['jobDescription'], "Agent Role")
        self.assertEqual(data['avatarImage'], "http://example.com/avatar.png")
        self.assertEqual(data['description'], "Agent Description")
        self.assertIn("prompt", data['agentData'])
        self.assertIn("llmConfig", data['agentData'])
        self.assertIn("models", data['agentData'])
        self.assertIn("resourcePools", data['agentData'])
        endpoint = self.client.api_service.post.call_args[1]['endpoint']
        self.assertIn("automaticPublish=true", endpoint)
        headers = self.client.api_service.post.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_create_agent_without_resource_pools(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_agent(
            project_id=self.project_id,
            name="Test Agent",
            access_scope="private",
            public_name="test-agent",
            job_description="Agent Role",
            avatar_image="http://example.com/avatar.png",
            description="Agent Description",
            agent_data_prompt={"instructions": "Do this task"},
            agent_data_llm_config={"maxTokens": 100},
            agent_data_models=[{"name": "gpt-4o"}],
            automatic_publish=False
        )

        self.client.api_service.post.assert_called_once()
        data = self.client.api_service.post.call_args[1]['data']['agentDefinition']
        self.assertNotIn("resourcePools", data['agentData'])
        self.assertEqual(result, {"status": "success"})

    def test_create_agent_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_agent(
            project_id=self.project_id,
            name="Test Agent",
            access_scope="private",
            public_name="test-agent",
            job_description="Agent Role",
            avatar_image="http://example.com/avatar.png",
            description="Agent Description",
            agent_data_prompt={"instructions": "Do this task"},
            agent_data_llm_config={"maxTokens": 100},
            agent_data_models=[{"name": "gpt-4o"}]
        )

        self.assertEqual(result, "success text")
        self.client.api_service.post.assert_called_once()

    def test_get_agent_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_agent(
            project_id=self.project_id,
            agent_id=self.agent_id,
            revision="1",
            version=2,
            allow_drafts=False
        )

        self.client.api_service.get.assert_called_once()
        params = self.client.api_service.get.call_args[1]['params']
        self.assertEqual(params['revision'], "1")
        self.assertEqual(params['version'], 2)
        self.assertFalse(params['allowDrafts'])
        headers = self.client.api_service.get.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_get_agent_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_agent(
            project_id=self.project_id,
            agent_id=self.agent_id
        )

        self.assertEqual(result, "success text")
        self.client.api_service.get.assert_called_once()

    def test_create_sharing_link_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.create_sharing_link(
            project_id=self.project_id,
            agent_id=self.agent_id
        )

        self.client.api_service.get.assert_called_once()
        headers = self.client.api_service.get.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_create_sharing_link_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.create_sharing_link(
            project_id=self.project_id,
            agent_id=self.agent_id
        )

        self.assertEqual(result, "success text")
        self.client.api_service.get.assert_called_once()

    def test_publish_agent_revision_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.publish_agent_revision(
            project_id=self.project_id,
            agent_id=self.agent_id,
            revision="2"
        )

        self.client.api_service.post.assert_called_once()
        data = self.client.api_service.post.call_args[1]['data']
        self.assertEqual(data['revision'], "2")
        headers = self.client.api_service.post.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_publish_agent_revision_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.publish_agent_revision(
            project_id=self.project_id,
            agent_id=self.agent_id,
            revision="2"
        )

        self.assertEqual(result, "success text")
        self.client.api_service.post.assert_called_once()

    def test_delete_agent_success(self):
        self.client.api_service.delete.return_value = self.mock_response

        result = self.client.delete_agent(
            project_id=self.project_id,
            agent_id=self.agent_id
        )

        self.client.api_service.delete.assert_called_once()
        headers = self.client.api_service.delete.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_delete_agent_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.delete.return_value = self.mock_response

        result = self.client.delete_agent(
            project_id=self.project_id,
            agent_id=self.agent_id
        )

        self.assertEqual(result, "success text")
        self.client.api_service.delete.assert_called_once()

    def test_update_agent_success(self):
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_agent(
            project_id=self.project_id,
            agent_id=self.agent_id,
            name="Updated Agent",
            access_scope="public",
            public_name="updated-agent",
            job_description="Updated Role",
            avatar_image="http://example.com/new-avatar.png",
            description="Updated Description",
            agent_data_prompt={"instructions": "Do this updated task"},
            agent_data_llm_config={"maxTokens": 200},
            agent_data_models=[{"name": "gpt-4o-updated"}],
            agent_data_resource_pools=[{"name": "pool2", "tools": [{"name": "tool2"}]}],
            automatic_publish=True,
            upsert=False
        )

        self.client.api_service.put.assert_called_once()
        data = self.client.api_service.put.call_args[1]['data']['agentDefinition']
        self.assertEqual(data['name'], "Updated Agent")
        self.assertEqual(data['accessScope'], "public")
        self.assertEqual(data['publicName'], "updated-agent")
        self.assertEqual(data['jobDescription'], "Updated Role")
        self.assertEqual(data['avatarImage'], "http://example.com/new-avatar.png")
        self.assertEqual(data['description'], "Updated Description")
        self.assertIn("prompt", data['agentData'])
        self.assertIn("llmConfig", data['agentData'])
        self.assertIn("models", data['agentData'])
        self.assertIn("resourcePools", data['agentData'])
        endpoint = self.client.api_service.put.call_args[1]['endpoint']
        self.assertIn("automaticPublish=true", endpoint)
        headers = self.client.api_service.put.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)
        self.assertEqual(result, {"status": "success"})

    def test_update_agent_with_upsert(self):
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_agent(
            project_id=self.project_id,
            agent_id=self.agent_id,
            name="Upserted Agent",
            access_scope="private",
            public_name="upserted-agent",
            job_description="Upserted Role",
            avatar_image="http://example.com/upsert-avatar.png",
            description="Upserted Description",
            agent_data_prompt={"instructions": "Do this upserted task"},
            agent_data_llm_config={"maxTokens": 150},
            agent_data_models=[{"name": "gpt-4o-upserted"}],
            automatic_publish=False,
            upsert=True
        )

        self.client.api_service.put.assert_called_once()
        endpoint = self.client.api_service.put.call_args[1]['endpoint']
        self.assertIn("upsert", endpoint)
        self.assertEqual(result, {"status": "success"})

    def test_update_agent_without_resource_pools(self):
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_agent(
            project_id=self.project_id,
            agent_id=self.agent_id,
            name="Updated Agent No Pools",
            access_scope="private",
            public_name="updated-agent-no-pools",
            job_description="Updated Role",
            avatar_image="http://example.com/avatar.png",
            description="Updated Description",
            agent_data_prompt={"instructions": "Do this task"},
            agent_data_llm_config={"maxTokens": 100},
            agent_data_models=[{"name": "gpt-4o"}],
            automatic_publish=False,
            upsert=False
        )

        self.client.api_service.put.assert_called_once()
        data = self.client.api_service.put.call_args[1]['data']['agentDefinition']
        self.assertNotIn("resourcePools", data['agentData'])
        self.assertEqual(result, {"status": "success"})

    def test_update_agent_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_agent(
            project_id=self.project_id,
            agent_id=self.agent_id,
            name="Updated Agent",
            access_scope="private",
            public_name="updated-agent",
            job_description="Updated Role",
            avatar_image="http://example.com/avatar.png",
            description="Updated Description",
            agent_data_prompt={"instructions": "Do this task"},
            agent_data_llm_config={"maxTokens": 100},
            agent_data_models=[{"name": "gpt-4o"}]
        )

        self.assertEqual(result, "success text")
        self.client.api_service.put.assert_called_once()

