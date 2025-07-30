import unittest
from unittest.mock import MagicMock, patch

from pygeai.core.base.responses import ErrorListResponse, EmptyResponse
from pygeai.lab.managers import AILabManager
from pygeai.lab.models import (
    FilterSettings, Agent, AgentList, AgentData, Prompt, LlmConfig, ModelList, Model, SharingLink,
    Tool, ToolList, ToolParameter, ReasoningStrategy, ReasoningStrategyList, LocalizedDescription, AgenticProcess,
    KnowledgeBase, Event, AgenticProcessList, ProcessInstanceList, Task, TaskList, Variable, ProcessInstance,
    KnowledgeBaseList, JobList
)


class TestAILabManager(unittest.TestCase):
    """
    python -m unittest pygeai.tests.lab.test_managers.TestAILabManager
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.base_url = "http://test-url.com"
        self.alias = "test_alias"
        self.manager = AILabManager(api_key=self.api_key, base_url=self.base_url, alias=self.alias)
        self.project_id = "proj123"

    # Agent-related Tests
    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.AgentMapper")
    def test_get_agent_list_success(self, mock_mapper, mock_client):
        """Test successful retrieval of agent list."""
        filter_settings = FilterSettings(status="active", start=0, count=10)
        mock_response = {"agents": [{"id": "agent1", "name": "Agent One"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_agents.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_agent_list.return_value = AgentList(agents=[])

        result = self.manager.get_agent_list(self.project_id, filter_settings)

        self.assertIsInstance(result, AgentList)
        mock_client.return_value.list_agents.assert_called_once_with(
            project_id=self.project_id,
            status="active",
            start=0,
            count=10,
            access_scope="private",
            allow_drafts=True,
            allow_external=False
        )
        mock_mapper.map_to_agent_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_agent_list_error(self, mock_error_handler, mock_client):
        """Test retrieval of agent list with API error."""
        filter_settings = FilterSettings(status="active")
        mock_response = {"errors": [{"code": "ERR001", "message": "API Error"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_agents.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_agent_list(self.project_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.AgentMapper")
    def test_create_agent_success(self, mock_mapper, mock_client):
        """Test successful creation of an agent."""
        agent = Agent(
            name="Test Agent",
            access_scope="public",
            public_name="com.globant.agent.test",
            job_description="Test Job",
            avatar_image="avatar.png",
            description="Test Description",
            agent_data=AgentData(
                prompt=Prompt(
                    instructions="Test Instructions",
                    inputs=["input1", "input2"]
                ),
                llm_config=LlmConfig(max_tokens=100),
                models=ModelList(models=[Model(name="model1")])
            )
        )
        mock_response = {"id": "agent123", "name": "Test Agent"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_agent.return_value = Agent(id="agent123", name="Test Agent", access_scope="public", public_name="com.globant.agent.test")

        result = self.manager.create_agent(self.project_id, agent, automatic_publish=True)

        self.assertIsInstance(result, Agent)
        mock_client.return_value.create_agent.assert_called_once()
        mock_mapper.map_to_agent.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_agent_error(self, mock_error_handler, mock_client):
        """Test agent creation with API error."""
        agent = Agent(
            name="Test Agent",
            access_scope="public",
            public_name="com.globant.agent.test"
        )
        mock_response = {"errors": [{"code": "ERR002", "message": "Creation Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_agent(self.project_id, agent)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.AgentMapper")
    def test_update_agent_success(self, mock_mapper, mock_client):
        """Test successful update of an agent."""
        agent = Agent(id="agent123", name="Updated Agent", access_scope="private")
        mock_response = {"id": "agent123", "name": "Updated Agent"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_agent.return_value = Agent(id="agent123", name="Updated Agent", access_scope="private")

        result = self.manager.update_agent(self.project_id, agent, automatic_publish=False, upsert=True)

        self.assertIsInstance(result, Agent)
        mock_client.return_value.update_agent.assert_called_once()
        mock_mapper.map_to_agent.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.AgentMapper")
    def test_get_agent_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific agent."""
        agent_id = "agent123"
        filter_settings = FilterSettings(revision="1", version=1, allow_drafts=True)
        mock_response = {"id": "agent123", "name": "Test Agent"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_agent.return_value = Agent(id="agent123", name="Test Agent", access_scope="private")

        result = self.manager.get_agent(self.project_id, agent_id, filter_settings)

        self.assertIsInstance(result, Agent)
        mock_client.return_value.get_agent.assert_called_once_with(
            project_id=self.project_id,
            agent_id=agent_id,
            revision="1",
            version=1,
            allow_drafts=True
        )
        mock_mapper.map_to_agent.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_agent_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific agent with API error."""
        agent_id = "agent123"
        filter_settings = FilterSettings(revision="1", version=1, allow_drafts=True)
        mock_response = {"errors": [{"code": "ERR003", "message": "Agent Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_agent(self.project_id, agent_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.AgentMapper")
    def test_create_sharing_link_success(self, mock_mapper, mock_client):
        """Test successful creation of a sharing link for an agent."""
        agent_id = "agent123"
        mock_response = {"agentId": "agent123", "apiToken": "token123", "sharedLink": "http://share.link"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_sharing_link.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_sharing_link.return_value = SharingLink(agent_id="agent123", api_token="token123",
                                                                   shared_link="http://share.link")

        result = self.manager.create_sharing_link(self.project_id, agent_id)

        self.assertIsInstance(result, SharingLink)
        mock_client.return_value.create_sharing_link.assert_called_once_with(
            project_id=self.project_id,
            agent_id=agent_id
        )
        mock_mapper.map_to_sharing_link.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_sharing_link_error(self, mock_error_handler, mock_client):
        """Test creation of a sharing link with API error."""
        agent_id = "agent123"
        mock_response = {"errors": [{"code": "ERR004", "message": "Sharing Link Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_sharing_link.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_sharing_link(self.project_id, agent_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.AgentMapper")
    def test_publish_agent_revision_success(self, mock_mapper, mock_client):
        """Test successful publishing of an agent revision."""
        agent_id = "agent123"
        revision = "2"
        mock_response = {"id": "agent123", "name": "Test Agent", "revision": 2}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_agent_revision.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_agent.return_value = Agent(id="agent123", name="Test Agent", access_scope="private")

        result = self.manager.publish_agent_revision(self.project_id, agent_id, revision)

        self.assertIsInstance(result, Agent)
        mock_client.return_value.publish_agent_revision.assert_called_once_with(
            project_id=self.project_id,
            agent_id=agent_id,
            revision=revision
        )
        mock_mapper.map_to_agent.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_publish_agent_revision_error(self, mock_error_handler, mock_client):
        """Test publishing of an agent revision with API error."""
        agent_id = "agent123"
        revision = "2"
        mock_response = {"errors": [{"code": "ERR005", "message": "Publish Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_agent_revision.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.publish_agent_revision(self.project_id, agent_id, revision)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_delete_agent_success(self, mock_mapper, mock_client):
        """Test successful deletion of an agent."""
        agent_id = "agent123"
        mock_response = {"status": "success"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.delete_agent(self.project_id, agent_id)

        self.assertIsInstance(result, EmptyResponse)
        mock_client.return_value.delete_agent.assert_called_once_with(
            project_id=self.project_id,
            agent_id=agent_id
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.AgentClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_delete_agent_error(self, mock_error_handler, mock_client):
        """Test deletion of an agent with API error."""
        agent_id = "agent123"
        mock_response = {"errors": [{"code": "ERR006", "message": "Delete Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_agent.return_value = mock_response
        self.manager._AILabManager__agent_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.delete_agent(self.project_id, agent_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    # Tool-related Tests
    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ToolMapper")
    def test_create_tool_success(self, mock_mapper, mock_client):
        """Test successful creation of a tool."""
        tool = Tool(
            name="Test Tool",
            description="A test tool",
            scope="api",
            open_api="http://api.spec",
            parameters=[ToolParameter(key="param1", data_type="String", description="Test param", is_required=True)]
        )
        mock_response = {"id": "tool123", "name": "Test Tool"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_tool.return_value = Tool(name="Test Tool", description="A test tool")

        result = self.manager.create_tool(self.project_id, tool, automatic_publish=True)

        self.assertIsInstance(result, Tool)
        mock_client.return_value.create_tool.assert_called_once()
        mock_mapper.map_to_tool.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_tool_error(self, mock_error_handler, mock_client):
        """Test creation of a tool with API error."""
        tool = Tool(
            name="Test Tool",
            description="A test tool",
            scope="api",
            open_api="http://api.spec"
        )
        mock_response = {"errors": [{"code": "ERR007", "message": "Tool Creation Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_tool(self.project_id, tool)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ToolMapper")
    def test_update_tool_success(self, mock_mapper, mock_client):
        """Test successful update of a tool."""
        tool = Tool(
            id="tool123",
            name="Updated Tool",
            description="An updated tool",
            scope="api",
            open_api="http://api.spec"
        )
        mock_response = {"id": "tool123", "name": "Updated Tool"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_tool.return_value = Tool(id="tool123", name="Updated Tool", description="An Updated Tool")

        result = self.manager.update_tool(self.project_id, tool, automatic_publish=False, upsert=True)

        self.assertIsInstance(result, Tool)
        mock_client.return_value.update_tool.assert_called_once()
        mock_mapper.map_to_tool.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_update_tool_error(self, mock_error_handler, mock_client):
        """Test update of a tool with API error."""
        tool = Tool(
            id="tool123",
            name="Updated Tool",
            description="An updated tool",
            scope="api",
            open_api="http://api.spec"
        )
        mock_response = {"errors": [{"code": "ERR008", "message": "Tool Update Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.update_tool(self.project_id, tool)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ToolMapper")
    def test_get_tool_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific tool."""
        tool_id = "tool123"
        filter_settings = FilterSettings(revision="1", version=1, allow_drafts=True)
        mock_response = {"id": "tool123", "name": "Test Tool"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_tool.return_value = Tool(id="tool123", name="Test Tool", description="Tool description")

        result = self.manager.get_tool(self.project_id, tool_id, filter_settings)

        self.assertIsInstance(result, Tool)
        mock_client.return_value.get_tool.assert_called_once_with(
            project_id=self.project_id,
            tool_id=tool_id,
            revision="1",
            version=1,
            allow_drafts=True
        )
        mock_mapper.map_to_tool.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_tool_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific tool with API error."""
        tool_id = "tool123"
        filter_settings = FilterSettings(revision="1", version=1, allow_drafts=True)
        mock_response = {"errors": [{"code": "ERR009", "message": "Tool Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_tool(self.project_id, tool_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_delete_tool_success(self, mock_mapper, mock_client):
        """Test successful deletion of a tool."""
        tool_id = "tool123"
        mock_response = {"status": "success"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.delete_tool(self.project_id, tool_id=tool_id)

        self.assertIsInstance(result, EmptyResponse)
        mock_client.return_value.delete_tool.assert_called_once_with(
            project_id=self.project_id,
            tool_id=tool_id,
            tool_name=None
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_delete_tool_error(self, mock_error_handler, mock_client):
        """Test deletion of a tool with API error."""
        tool_id = "tool123"
        mock_response = {"errors": [{"code": "ERR010", "message": "Delete Tool Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_tool.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.delete_tool(self.project_id, tool_id=tool_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_delete_tool_validation_error(self):
        """Test deletion of a tool with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.delete_tool(self.project_id)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ToolMapper")
    def test_list_tools_success(self, mock_mapper, mock_client):
        """Test successful retrieval of tool list."""
        filter_settings = FilterSettings(id="tool1", count="50", scope="api")
        mock_response = {"tools": [{"id": "tool1", "name": "Tool One"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_tools.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_tool_list.return_value = ToolList(tools=[])

        result = self.manager.list_tools(self.project_id, filter_settings)

        self.assertIsInstance(result, ToolList)
        mock_client.return_value.list_tools.assert_called_once()
        mock_mapper.map_to_tool_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_tools_error(self, mock_error_handler, mock_client):
        """Test retrieval of tool list with API error."""
        filter_settings = FilterSettings(id="tool1", count="50", scope="api")
        mock_response = {"errors": [{"code": "ERR011", "message": "List Tools Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_tools.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_tools(self.project_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ToolMapper")
    def test_publish_tool_revision_success(self, mock_mapper, mock_client):
        """Test successful publishing of a tool revision."""
        tool_id = "tool123"
        revision = "2"
        mock_response = {"id": "tool123", "name": "Test Tool", "revision": 2}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_tool_revision.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_tool.return_value = Tool(id="tool123", name="Test Tool", description="Tool description")

        result = self.manager.publish_tool_revision(self.project_id, tool_id, revision)

        self.assertIsInstance(result, Tool)
        mock_client.return_value.publish_tool_revision.assert_called_once_with(
            project_id=self.project_id,
            tool_id=tool_id,
            revision=revision
        )
        mock_mapper.map_to_tool.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_publish_tool_revision_error(self, mock_error_handler, mock_client):
        """Test publishing of a tool revision with API error."""
        tool_id = "tool123"
        revision = "2"
        mock_response = {"errors": [{"code": "ERR012", "message": "Publish Tool Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_tool_revision.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.publish_tool_revision(self.project_id, tool_id, revision)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ToolMapper")
    def test_get_parameter_success(self, mock_mapper, mock_client):
        """Test successful retrieval of tool parameters."""
        tool_id = "tool123"
        filter_settings = FilterSettings(revision="1", version=1, allow_drafts=True)
        mock_response = [{"key": "param1", "dataType": "String"}]
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_parameter.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_parameter_list.return_value = [
            ToolParameter(key="param1", data_type="String", description="", is_required=False)]

        result = self.manager.get_parameter(self.project_id, tool_id=tool_id, filter_settings=filter_settings)

        self.assertIsInstance(result, list)
        mock_client.return_value.get_parameter.assert_called_once_with(
            project_id=self.project_id,
            tool_id=tool_id,
            tool_public_name=None,
            revision="1",
            version=1,
            allow_drafts=True
        )
        mock_mapper.map_to_parameter_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_parameter_error(self, mock_error_handler, mock_client):
        """Test retrieval of tool parameters with API error."""
        tool_id = "tool123"
        filter_settings = FilterSettings(revision="1", version=1, allow_drafts=True)
        mock_response = {"errors": [{"code": "ERR013", "message": "Get Parameters Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_parameter.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_parameter(self.project_id, tool_id=tool_id, filter_settings=filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_parameter_validation_error(self):
        """Test retrieval of tool parameters with missing ID and public name."""
        with self.assertRaises(ValueError):
            self.manager.get_parameter(self.project_id)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_set_parameter_success(self, mock_mapper, mock_client):
        """Test successful setting of tool parameters."""
        tool_id = "tool123"
        parameters = [ToolParameter(key="param1", data_type="String", description="Test param", is_required=True)]
        mock_response = {"status": "success"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.set_parameter.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.set_parameter(self.project_id, tool_id=tool_id, parameters=parameters)

        self.assertIsInstance(result, EmptyResponse)
        mock_client.return_value.set_parameter.assert_called_once()
        mock_mapper.map_to_empty_response.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ToolClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_set_parameter_error(self, mock_error_handler, mock_client):
        """Test setting of tool parameters with API error."""
        tool_id = "tool123"
        parameters = [ToolParameter(key="param1", data_type="String", description="Test param", is_required=True)]
        mock_response = {"errors": [{"code": "ERR014", "message": "Set Parameters Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.set_parameter.return_value = mock_response
        self.manager._AILabManager__tool_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.set_parameter(self.project_id, tool_id=tool_id, parameters=parameters)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_set_parameter_validation_error(self):
        """Test setting tool parameters with missing ID and public name or parameters."""
        with self.assertRaises(ValueError):
            self.manager.set_parameter(self.project_id)
        with self.assertRaises(ValueError):
            self.manager.set_parameter(self.project_id, tool_id="tool123", parameters=[])

    # Reasoning Strategy-related Tests
    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ReasoningStrategyMapper")
    def test_list_reasoning_strategies_success(self, mock_mapper, mock_client):
        """Test successful retrieval of reasoning strategies list."""
        filter_settings = FilterSettings(start=0, count="50", access_scope="public")
        mock_response = {"strategies": [{"id": "strat1", "name": "Strategy One"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_reasoning_strategies.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_mapper.map_to_reasoning_strategy_list.return_value = ReasoningStrategyList(strategies=[])

        result = self.manager.list_reasoning_strategies(filter_settings)

        self.assertIsInstance(result, ReasoningStrategyList)
        mock_client.return_value.list_reasoning_strategies.assert_called_once()
        mock_mapper.map_to_reasoning_strategy_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_reasoning_strategies_error(self, mock_error_handler, mock_client):
        """Test retrieval of reasoning strategies list with API error."""
        filter_settings = FilterSettings(start=0, count="50", access_scope="public")
        mock_response = {"errors": [{"code": "ERR015", "message": "List Strategies Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_reasoning_strategies.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_reasoning_strategies(filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ReasoningStrategyMapper")
    def test_create_reasoning_strategy_success(self, mock_mapper, mock_client):
        """Test successful creation of a reasoning strategy."""
        strategy = ReasoningStrategy(
            name="Test Strategy",
            system_prompt="Test Prompt",
            access_scope="private",
            type="addendum",
            localized_descriptions=[LocalizedDescription(language="en", description="Test Desc")]
        )
        mock_response = {"id": "strat123", "name": "Test Strategy"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_reasoning_strategy.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_mapper.map_to_reasoning_strategy.return_value = ReasoningStrategy(name="Test Strategy",
                                                                               access_scope="private", type="addendum")

        result = self.manager.create_reasoning_strategy(self.project_id, strategy, automatic_publish=True)

        self.assertIsInstance(result, ReasoningStrategy)
        mock_client.return_value.create_reasoning_strategy.assert_called_once()
        mock_mapper.map_to_reasoning_strategy.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_reasoning_strategy_error(self, mock_error_handler, mock_client):
        """Test creation of a reasoning strategy with API error."""
        strategy = ReasoningStrategy(
            name="Test Strategy",
            system_prompt="Test Prompt",
            access_scope="private",
            type="addendum",
            localized_descriptions=[LocalizedDescription(language="en", description="Test Desc")]
        )
        mock_response = {"errors": [{"code": "ERR016", "message": "Create Strategy Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_reasoning_strategy.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_reasoning_strategy(self.project_id, strategy)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ReasoningStrategyMapper")
    def test_update_reasoning_strategy_success(self, mock_mapper, mock_client):
        """Test successful update of a reasoning strategy."""
        strategy = ReasoningStrategy(
            id="strat123",
            name="Updated Strategy",
            system_prompt="Updated Prompt",
            access_scope="private",
            type="addendum",
            localized_descriptions=[LocalizedDescription(language="en", description="Updated Desc")]
        )
        mock_response = {"id": "strat123", "name": "Updated Strategy"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_reasoning_strategy.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_mapper.map_to_reasoning_strategy.return_value = ReasoningStrategy(name="Updated Strategy",
                                                                               access_scope="private", type="addendum")

        result = self.manager.update_reasoning_strategy(self.project_id, strategy, automatic_publish=False, upsert=True)

        self.assertIsInstance(result, ReasoningStrategy)
        mock_client.return_value.update_reasoning_strategy.assert_called_once()
        mock_mapper.map_to_reasoning_strategy.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_update_reasoning_strategy_error(self, mock_error_handler, mock_client):
        """Test update of a reasoning strategy with API error."""
        strategy = ReasoningStrategy(
            id="strat123",
            name="Updated Strategy",
            system_prompt="Updated Prompt",
            access_scope="private",
            type="addendum",
            localized_descriptions=[LocalizedDescription(language="en", description="Updated Desc")]
        )
        mock_response = {"errors": [{"code": "ERR017", "message": "Update Strategy Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_reasoning_strategy.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.update_reasoning_strategy(self.project_id, strategy)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ReasoningStrategyMapper")
    def test_get_reasoning_strategy_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific reasoning strategy."""
        strategy_id = "strat123"
        mock_response = {"id": "strat123", "name": "Test Strategy"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_reasoning_strategy.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_mapper.map_to_reasoning_strategy.return_value = ReasoningStrategy(name="Test Strategy",
                                                                               access_scope="private", type="addendum")

        result = self.manager.get_reasoning_strategy(self.project_id, reasoning_strategy_id=strategy_id)

        self.assertIsInstance(result, ReasoningStrategy)
        mock_client.return_value.get_reasoning_strategy.assert_called_once_with(
            project_id=self.project_id,
            reasoning_strategy_id=strategy_id,
            reasoning_strategy_name=None
        )
        mock_mapper.map_to_reasoning_strategy.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.ReasoningStrategyClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_reasoning_strategy_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific reasoning strategy with API error."""
        strategy_id = "strat123"
        mock_response = {"errors": [{"code": "ERR018", "message": "Strategy Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_reasoning_strategy.return_value = mock_response
        self.manager._AILabManager__reasoning_strategy_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_reasoning_strategy(self.project_id, reasoning_strategy_id=strategy_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_reasoning_strategy_validation_error(self):
        """Test retrieval of reasoning strategy with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.get_reasoning_strategy(self.project_id)

    # Process-related Tests
    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.AgenticProcessMapper")
    def test_create_process_success(self, mock_mapper, mock_client):
        """Test successful creation of a process."""
        process = AgenticProcess(
            key="proc_key",
            name="Test Process",
            description="A test process",
            kb=KnowledgeBase(name="Test KB"),
            start_event=Event(key="start", name="Start"),
            end_event=Event(key="end", name="End")
        )
        mock_response = {"id": "proc123", "name": "Test Process"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_agentic_process.return_value = AgenticProcess(name="Test Process")

        result = self.manager.create_process(self.project_id, process, automatic_publish=True)

        self.assertIsInstance(result, AgenticProcess)
        mock_client.return_value.create_process.assert_called_once()
        mock_mapper.map_to_agentic_process.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_process_error(self, mock_error_handler, mock_client):
        """Test creation of a process with API error."""
        process = AgenticProcess(
            key="proc_key",
            name="Test Process",
            description="A test process"
        )
        mock_response = {"errors": [{"code": "ERR019", "message": "Process Creation Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_process(self.project_id, process)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.AgenticProcessMapper")
    def test_update_process_success(self, mock_mapper, mock_client):
        """Test successful update of a process."""
        process = AgenticProcess(
            id="proc123",
            name="Updated Process",
            key="proc_key",
            description="An updated process"
        )
        mock_response = {"id": "proc123", "name": "Updated Process"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_agentic_process.return_value = AgenticProcess(name="Updated Process")

        result = self.manager.update_process(self.project_id, process, automatic_publish=False, upsert=True)

        self.assertIsInstance(result, AgenticProcess)
        mock_client.return_value.update_process.assert_called_once()
        mock_mapper.map_to_agentic_process.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_update_process_error(self, mock_error_handler, mock_client):
        """Test update of a process with API error."""
        process = AgenticProcess(
            id="proc123",
            name="Updated Process",
            key="proc_key"
        )
        mock_response = {"errors": [{"code": "ERR020", "message": "Process Update Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.update_process(self.project_id, process)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.AgenticProcessMapper")
    def test_get_process_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific process."""
        process_id = "proc123"
        filter_settings = FilterSettings(revision="1", version=0, allow_drafts=True)
        mock_response = {"id": "proc123", "name": "Test Process"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_agentic_process.return_value = AgenticProcess(name="Test Process")

        result = self.manager.get_process(self.project_id, process_id=process_id, filter_settings=filter_settings)

        self.assertIsInstance(result, AgenticProcess)
        mock_client.return_value.get_process.assert_called_once_with(
            project_id=self.project_id,
            process_id=process_id,
            process_name=None,
            revision="1",
            version=0,
            allow_drafts=True
        )
        mock_mapper.map_to_agentic_process.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_process_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific process with API error."""
        process_id = "proc123"
        mock_response = {"errors": [{"code": "ERR021", "message": "Process Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_process(self.project_id, process_id=process_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_process_validation_error(self):
        """Test retrieval of process with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.get_process(self.project_id)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.AgenticProcessMapper")
    def test_list_processes_success(self, mock_mapper, mock_client):
        """Test successful retrieval of process list."""
        filter_settings = FilterSettings(start=0, count="50", allow_drafts=True)
        mock_response = {"processes": [{"id": "proc1", "name": "Process One"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_processes.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_agentic_process_list.return_value = AgenticProcessList(processes=[])

        result = self.manager.list_processes(self.project_id, filter_settings)

        self.assertIsInstance(result, AgenticProcessList)
        mock_client.return_value.list_processes.assert_called_once()
        mock_mapper.map_to_agentic_process_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_processes_error(self, mock_error_handler, mock_client):
        """Test retrieval of process list with API error."""
        filter_settings = FilterSettings(start=0, count="50", allow_drafts=True)
        mock_response = {"errors": [{"code": "ERR022", "message": "List Processes Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_processes.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_processes(self.project_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ProcessInstanceMapper")
    def test_list_process_instances_success(self, mock_mapper, mock_client):
        """Test successful retrieval of process instances list."""
        process_id = "proc123"
        filter_settings = FilterSettings(start=0, count=10, is_active=True)
        mock_response = {"instances": [{"id": "inst1", "subject": "Test Instance"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_process_instances.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_process_instance_list.return_value = ProcessInstanceList(instances=[])

        result = self.manager.list_process_instances(self.project_id, process_id, filter_settings)

        self.assertIsInstance(result, ProcessInstanceList)
        mock_client.return_value.list_process_instances.assert_called_once_with(
            project_id=self.project_id,
            process_id=process_id,
            is_active=True,
            start=0,
            count=10
        )
        mock_mapper.map_to_process_instance_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_process_instances_error(self, mock_error_handler, mock_client):
        """Test retrieval of process instances list with API error."""
        process_id = "proc123"
        filter_settings = FilterSettings(start=0, count=10, is_active=True)
        mock_response = {"errors": [{"code": "ERR023", "message": "List Instances Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_process_instances.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_process_instances(self.project_id, process_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_delete_process_success(self, mock_mapper, mock_client):
        """Test successful deletion of a process."""
        process_id = "proc123"
        mock_response = {"status": "success"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.delete_process(self.project_id, process_id=process_id)

        self.assertIsInstance(result, EmptyResponse)
        mock_client.return_value.delete_process.assert_called_once_with(
            project_id=self.project_id,
            process_id=process_id,
            process_name=None
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_delete_process_error(self, mock_error_handler, mock_client):
        """Test deletion of a process with API error."""
        process_id = "proc123"
        mock_response = {"errors": [{"code": "ERR024", "message": "Delete Process Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_process.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.delete_process(self.project_id, process_id=process_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_delete_process_validation_error(self):
        """Test deletion of process with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.delete_process(self.project_id)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.AgenticProcessMapper")
    def test_publish_process_revision_success(self, mock_mapper, mock_client):
        """Test successful publishing of a process revision."""
        process_id = "proc123"
        revision = "2"
        mock_response = {"id": "proc123", "name": "Test Process", "revision": 2}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_process_revision.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_agentic_process.return_value = AgenticProcess(name="Test Process")

        result = self.manager.publish_process_revision(self.project_id, process_id=process_id, revision=revision)

        self.assertIsInstance(result, AgenticProcess)
        mock_client.return_value.publish_process_revision.assert_called_once_with(
            project_id=self.project_id,
            process_id=process_id,
            process_name=None,
            revision=revision
        )
        mock_mapper.map_to_agentic_process.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_publish_process_revision_error(self, mock_error_handler, mock_client):
        """Test publishing of a process revision with API error."""
        process_id = "proc123"
        revision = "2"
        mock_response = {"errors": [{"code": "ERR025", "message": "Publish Process Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_process_revision.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.publish_process_revision(self.project_id, process_id=process_id, revision=revision)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_publish_process_revision_validation_error(self):
        """Test publishing of process revision with missing ID, name, or revision."""
        with self.assertRaises(ValueError):
            self.manager.publish_process_revision(self.project_id)
        with self.assertRaises(ValueError):
            self.manager.publish_process_revision(self.project_id, process_id="proc123")

    # Task-related Tests
    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.TaskMapper")
    def test_create_task_success(self, mock_mapper, mock_client):
        """Test successful creation of a task."""
        task = Task(name="Test Task", description="A test task")
        mock_response = {"id": "task123", "name": "Test Task"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_task.return_value = Task(name="Test Task")

        result = self.manager.create_task(self.project_id, task, automatic_publish=True)

        self.assertIsInstance(result, Task)
        mock_client.return_value.create_task.assert_called_once()
        mock_mapper.map_to_task.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_task_error(self, mock_error_handler, mock_client):
        """Test creation of a task with API error."""
        task = Task(name="Test Task", description="A test task")
        mock_response = {"errors": [{"code": "ERR026", "message": "Task Creation Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.create_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_task(self.project_id, task)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.TaskMapper")
    def test_get_task_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific task."""
        task_id = "task123"
        mock_response = {"id": "task123", "name": "Test Task"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_task.return_value = Task(name="Test Task")

        result = self.manager.get_task(self.project_id, task_id=task_id)

        self.assertIsInstance(result, Task)
        mock_client.return_value.get_task.assert_called_once_with(
            project_id=self.project_id,
            task_id=task_id,
            task_name=None
        )
        mock_mapper.map_to_task.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_task_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific task with API error."""
        task_id = "task123"
        mock_response = {"errors": [{"code": "ERR027", "message": "Task Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_task(self.project_id, task_id=task_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_task_validation_error(self):
        """Test retrieval of task with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.get_task(self.project_id)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.TaskMapper")
    def test_list_tasks_success(self, mock_mapper, mock_client):
        """Test successful retrieval of task list."""
        filter_settings = FilterSettings(start=0, count="50", allow_drafts=True)
        mock_response = {"tasks": [{"id": "task1", "name": "Task One"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_tasks.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_task_list.return_value = TaskList(tasks=[])

        result = self.manager.list_tasks(self.project_id, filter_settings)

        self.assertIsInstance(result, TaskList)
        mock_client.return_value.list_tasks.assert_called_once()
        mock_mapper.map_to_task_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_tasks_error(self, mock_error_handler, mock_client):
        """Test retrieval of task list with API error."""
        filter_settings = FilterSettings(start=0, count="50", allow_drafts=True)
        mock_response = {"errors": [{"code": "ERR028", "message": "List Tasks Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.list_tasks.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_tasks(self.project_id, filter_settings)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.TaskMapper")
    def test_update_task_success(self, mock_mapper, mock_client):
        """Test successful update of a task."""
        task = Task(id="task123", name="Updated Task", description="An updated task")
        mock_response = {"id": "task123", "name": "Updated Task"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_task.return_value = Task(name="Updated Task")

        result = self.manager.update_task(self.project_id, task, automatic_publish=False, upsert=True)

        self.assertIsInstance(result, Task)
        mock_client.return_value.update_task.assert_called_once()
        mock_mapper.map_to_task.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_update_task_error(self, mock_error_handler, mock_client):
        """Test update of a task with API error."""
        task = Task(id="task123", name="Updated Task", description="An updated task")
        mock_response = {"errors": [{"code": "ERR029", "message": "Task Update Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.update_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.update_task(self.project_id, task)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_update_task_validation_error(self):
        """Test update of task with missing ID."""
        task = Task(name="Updated Task")
        with self.assertRaises(ValueError):
            self.manager.update_task(self.project_id, task)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_delete_task_success(self, mock_mapper, mock_client):
        """Test successful deletion of a task."""
        task_id = "task123"
        mock_response = {"status": "success"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.delete_task(self.project_id, task_id=task_id)

        self.assertIsInstance(result, EmptyResponse)
        mock_client.return_value.delete_task.assert_called_once_with(
            project_id=self.project_id,
            task_id=task_id,
            task_name=None
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_delete_task_error(self, mock_error_handler, mock_client):
        """Test deletion of a task with API error."""
        task_id = "task123"
        mock_response = {"errors": [{"code": "ERR030", "message": "Delete Task Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.delete_task.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.delete_task(self.project_id, task_id=task_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_delete_task_validation_error(self):
        """Test deletion of task with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.delete_task(self.project_id)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.TaskMapper")
    def test_publish_task_revision_success(self, mock_mapper, mock_client):
        """Test successful publishing of a task revision."""
        task_id = "task123"
        revision = "2"
        mock_response = {"id": "task123", "name": "Test Task", "revision": 2}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_task_revision.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_task.return_value = Task(name="Test Task")

        result = self.manager.publish_task_revision(self.project_id, task_id=task_id, revision=revision)

        self.assertIsInstance(result, Task)
        mock_client.return_value.publish_task_revision.assert_called_once_with(
            project_id=self.project_id,
            task_id=task_id,
            task_name=None,
            revision=revision
        )
        mock_mapper.map_to_task.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_publish_task_revision_error(self, mock_error_handler, mock_client):
        """Test publishing of a task revision with API error."""
        task_id = "task123"
        revision = "2"
        mock_response = {"errors": [{"code": "ERR031", "message": "Publish Task Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.publish_task_revision.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.publish_task_revision(self.project_id, task_id=task_id, revision=revision)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_publish_task_revision_validation_error(self):
        """Test publishing of task revision with missing ID, name, or revision."""
        with self.assertRaises(ValueError):
            self.manager.publish_task_revision(self.project_id)
        with self.assertRaises(ValueError):
            self.manager.publish_task_revision(self.project_id, task_id="task123")

    # Instance-related Tests
    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ProcessInstanceMapper")
    def test_start_instance_success(self, mock_mapper, mock_client):
        """Test successful starting of a process instance."""
        process_name = "Test Process"
        subject = "Test Subject"
        variables = [Variable(key="var1", value="value1")]
        mock_response = {"id": "inst123", "subject": "Test Subject"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.start_instance.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_process_instance.return_value = ProcessInstance(subject="Test Subject",
                                                                           process=AgenticProcess(name="Test Process"))

        result = self.manager.start_instance(self.project_id, process_name, subject, variables)

        self.assertIsInstance(result, ProcessInstance)
        mock_client.return_value.start_instance.assert_called_once()
        mock_mapper.map_to_process_instance.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_start_instance_error(self, mock_error_handler, mock_client):
        """Test starting of a process instance with API error."""
        process_name = "Test Process"
        subject = "Test Subject"
        mock_response = {"errors": [{"code": "ERR032", "message": "Start Instance Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.start_instance.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.start_instance(self.project_id, process_name, subject)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_abort_instance_success(self, mock_mapper, mock_client):
        """Test successful abortion of a process instance."""
        instance_id = "inst123"
        mock_response = {"status": "success"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.abort_instance.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.abort_instance(self.project_id, instance_id)

        self.assertIsInstance(result, EmptyResponse)
        mock_client.return_value.abort_instance.assert_called_once_with(
            project_id=self.project_id,
            instance_id=instance_id
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_abort_instance_error(self, mock_error_handler, mock_client):
        """Test abortion of a process instance with API error."""
        instance_id = "inst123"
        mock_response = {"errors": [{"code": "ERR033", "message": "Abort Instance Failed"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.abort_instance.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.abort_instance(self.project_id, instance_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_abort_instance_validation_error(self):
        """Test abortion of instance with missing ID."""
        with self.assertRaises(ValueError):
            self.manager.abort_instance(self.project_id, "")

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ProcessInstanceMapper")
    def test_get_instance_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific instance."""
        instance_id = "inst123"
        mock_response = {"id": "inst123", "subject": "Test Instance"}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_instance.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_mapper.map_to_process_instance.return_value = ProcessInstance(subject="Test Instance",
                                                                           process=AgenticProcess(name="Test Process"))

        result = self.manager.get_instance(self.project_id, instance_id)

        self.assertIsInstance(result, ProcessInstance)
        mock_client.return_value.get_instance.assert_called_once_with(
            project_id=self.project_id,
            instance_id=instance_id
        )
        mock_mapper.map_to_process_instance.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_instance_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific instance with API error."""
        instance_id = "inst123"
        mock_response = {"errors": [{"code": "ERR034", "message": "Instance Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_instance.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_instance(self.project_id, instance_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_instance_validation_error(self):
        """Test retrieval of instance with missing ID."""
        with self.assertRaises(ValueError):
            self.manager.get_instance(self.project_id, "")

    @patch("pygeai.lab.managers.AgenticProcessClient")
    def test_get_instance_history_success(self, mock_client):
        """Test successful retrieval of instance history."""
        instance_id = "inst123"
        mock_response = {"history": [{"event": "start", "time": "2023-01-01"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_instance_history.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value

        result = self.manager.get_instance_history(self.project_id, instance_id)

        self.assertIsInstance(result, dict)
        mock_client.return_value.get_instance_history.assert_called_once_with(
            project_id=self.project_id,
            instance_id=instance_id
        )

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_instance_history_error(self, mock_error_handler, mock_client):
        """Test retrieval of instance history with API error."""
        instance_id = "inst123"
        mock_response = {"errors": [{"code": "ERR035", "message": "Instance History Not Found"}]}
        mock_client.return_value = MagicMock()
        mock_client.return_value.get_instance_history.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client.return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_instance_history(self.project_id, instance_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_instance_history_validation_error(self):
        """Test retrieval of instance history with missing ID."""
        with self.assertRaises(ValueError):
            self.manager.get_instance_history(self.project_id, "")

    @patch("pygeai.lab.managers.AgenticProcessClient")
    def test_get_thread_information_success(self, mock_client):
        """Test successful retrieval of thread information."""
        thread_id = "thread123"
        mock_response = {"threadId": "thread123", "status": "active"}
        mock_client_return_value = MagicMock()
        mock_client_return_value.get_thread_information.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value

        result = self.manager.get_thread_information(self.project_id, thread_id)

        self.assertIsInstance(result, dict)
        mock_client_return_value.get_thread_information.assert_called_once_with(
            project_id=self.project_id,
            thread_id=thread_id
        )

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_thread_information_error(self, mock_error_handler, mock_client):
        """Test retrieval of thread information with API error."""
        thread_id = "thread123"
        mock_response = {"errors": [{"code": "ERR036", "message": "Thread Not Found"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.get_thread_information.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_thread_information(self.project_id, thread_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_thread_information_validation_error(self):
        """Test retrieval of thread information with missing ID."""
        with self.assertRaises(ValueError):
            self.manager.get_thread_information(self.project_id, "")

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_send_user_signal_success(self, mock_mapper, mock_client):
        """Test successful sending of a user signal to a process instance."""
        instance_id = "inst123"
        signal_name = "user_signal"
        mock_response = {"status": "success"}
        mock_client_return_value = MagicMock()
        mock_client_return_value.send_user_signal.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.send_user_signal(self.project_id, instance_id, signal_name)

        self.assertIsInstance(result, EmptyResponse)
        mock_client_return_value.send_user_signal.assert_called_once_with(
            project_id=self.project_id,
            instance_id=instance_id,
            signal_name=signal_name
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_send_user_signal_error(self, mock_error_handler, mock_client):
        """Test sending of a user signal with API error."""
        instance_id = "inst123"
        signal_name = "user_signal"
        mock_response = {"errors": [{"code": "ERR037", "message": "Send Signal Failed"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.send_user_signal.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.send_user_signal(self.project_id, instance_id, signal_name)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_send_user_signal_validation_error(self):
        """Test sending of user signal with missing instance ID or signal name."""
        with self.assertRaises(ValueError):
            self.manager.send_user_signal(self.project_id, "", "signal")
        with self.assertRaises(ValueError):
            self.manager.send_user_signal(self.project_id, "inst123", "")

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.KnowledgeBaseMapper")
    def test_create_knowledge_base_success(self, mock_mapper, mock_client):
        """Test successful creation of a knowledge base."""
        kb = KnowledgeBase(name="Test KB", artifact_type_name=["type1", "type2"])
        mock_response = {"id": "kb123", "name": "Test KB"}
        mock_client_return_value = MagicMock()
        mock_client_return_value.create_kb.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_mapper.map_to_knowledge_base.return_value = KnowledgeBase(name="Test KB")

        result = self.manager.create_knowledge_base(self.project_id, kb)

        self.assertIsInstance(result, KnowledgeBase)
        mock_client_return_value.create_kb.assert_called_once_with(
            project_id=self.project_id,
            name="Test KB",
            artifacts=None,
            metadata=None
        )
        mock_mapper.map_to_knowledge_base.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_create_knowledge_base_error(self, mock_error_handler, mock_client):
        """Test creation of a knowledge base with API error."""
        kb = KnowledgeBase(name="Test KB", artifact_type_name=["type1", "type2"])
        mock_response = {"errors": [{"code": "ERR038", "message": "Knowledge Base Creation Failed"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.create_kb.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.create_knowledge_base(self.project_id, kb)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.KnowledgeBaseMapper")
    def test_list_knowledge_bases_success(self, mock_mapper, mock_client):
        """Test successful retrieval of knowledge base list."""
        name = "Test KB"
        start = 0
        count = 5
        mock_response = {"knowledgeBases": [{"id": "kb1", "name": "Test KB"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.list_kbs.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_mapper.map_to_knowledge_base_list.return_value = KnowledgeBaseList(knowledge_bases=[])

        result = self.manager.list_knowledge_bases(self.project_id, name, start, count)

        self.assertIsInstance(result, KnowledgeBaseList)
        mock_client_return_value.list_kbs.assert_called_once_with(
            project_id=self.project_id,
            name=name,
            start=start,
            count=count
        )
        mock_mapper.map_to_knowledge_base_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_knowledge_bases_error(self, mock_error_handler, mock_client):
        """Test retrieval of knowledge base list with API error."""
        name = "Test KB"
        start = 0
        count = 5
        mock_response = {"errors": [{"code": "ERR039", "message": "List Knowledge Bases Failed"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.list_kbs.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_knowledge_bases(self.project_id, name, start, count)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.KnowledgeBaseMapper")
    def test_get_knowledge_base_success(self, mock_mapper, mock_client):
        """Test successful retrieval of a specific knowledge base."""
        kb_id = "kb123"
        mock_response = {"id": "kb123", "name": "Test KB"}
        mock_client_return_value = MagicMock()
        mock_client_return_value.get_kb.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_mapper.map_to_knowledge_base.return_value = KnowledgeBase(name="Test KB")

        result = self.manager.get_knowledge_base(self.project_id, kb_id=kb_id)

        self.assertIsInstance(result, KnowledgeBase)
        mock_client_return_value.get_kb.assert_called_once_with(
            project_id=self.project_id,
            kb_name=None,
            kb_id=kb_id
        )
        mock_mapper.map_to_knowledge_base.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_get_knowledge_base_error(self, mock_error_handler, mock_client):
        """Test retrieval of a specific knowledge base with API error."""
        kb_id = "kb123"
        mock_response = {"errors": [{"code": "ERR040", "message": "Knowledge Base Not Found"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.get_kb.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.get_knowledge_base(self.project_id, kb_id=kb_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_get_knowledge_base_validation_error(self):
        """Test retrieval of knowledge base with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.get_knowledge_base(self.project_id)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ResponseMapper")
    def test_delete_knowledge_base_success(self, mock_mapper, mock_client):
        """Test successful deletion of a knowledge base."""
        kb_id = "kb123"
        mock_response = {"status": "success"}
        mock_client_return_value = MagicMock()
        mock_client_return_value.delete_kb.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_mapper.map_to_empty_response.return_value = EmptyResponse()

        result = self.manager.delete_knowledge_base(self.project_id, kb_id=kb_id)

        self.assertIsInstance(result, EmptyResponse)
        mock_client_return_value.delete_kb.assert_called_once_with(
            project_id=self.project_id,
            kb_name=None,
            kb_id=kb_id
        )
        mock_mapper.map_to_empty_response.assert_called_once()

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_delete_knowledge_base_error(self, mock_error_handler, mock_client):
        """Test deletion of a knowledge base with API error."""
        kb_id = "kb123"
        mock_response = {"errors": [{"code": "ERR041", "message": "Delete Knowledge Base Failed"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.delete_kb.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.delete_knowledge_base(self.project_id, kb_id=kb_id)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_delete_knowledge_base_validation_error(self):
        """Test deletion of knowledge base with missing ID and name."""
        with self.assertRaises(ValueError):
            self.manager.delete_knowledge_base(self.project_id)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.JobMapper")
    def test_list_jobs_success(self, mock_mapper, mock_client):
        """Test successful retrieval of job list."""
        filter_settings = FilterSettings(start=0, count=20)
        topic = "Default"
        token = "token123"
        mock_response = {"jobs": [{"token": "token123", "name": "Job One"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.list_jobs.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_mapper.map_to_job_list.return_value = JobList(jobs=[])

        result = self.manager.list_jobs(self.project_id, filter_settings, topic, token)

        self.assertIsInstance(result, JobList)
        mock_client_return_value.list_jobs.assert_called_once_with(
            project_id=self.project_id,
            start=0,
            count=20,
            topic=topic,
            token=token,
            name=None
        )
        mock_mapper.map_to_job_list.assert_called_once_with(mock_response)

    @patch("pygeai.lab.managers.AgenticProcessClient")
    @patch("pygeai.lab.managers.ErrorHandler")
    def test_list_jobs_error(self, mock_error_handler, mock_client):
        """Test retrieval of job list with API error."""
        filter_settings = FilterSettings(start=0, count=20)
        topic = "Default"
        token = "token123"
        mock_response = {"errors": [{"code": "ERR042", "message": "List Jobs Failed"}]}
        mock_client_return_value = MagicMock()
        mock_client_return_value.list_jobs.return_value = mock_response
        self.manager._AILabManager__process_client = mock_client_return_value
        mock_error_handler.has_errors.return_value = True
        mock_error_handler.extract_error.return_value = ErrorListResponse(errors=[])

        result = self.manager.list_jobs(self.project_id, filter_settings, topic, token)

        self.assertIsInstance(result, ErrorListResponse)
        mock_error_handler.has_errors.assert_called_once_with(mock_response)
        mock_error_handler.extract_error.assert_called_once_with(mock_response)

    def test_list_jobs_validation_error(self):
        """Test retrieval of job list with missing project ID."""
        with self.assertRaises(ValueError):
            self.manager.list_jobs("")
