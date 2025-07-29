import unittest
from unittest.mock import MagicMock
from json import JSONDecodeError
from pygeai.lab.tools.clients import ToolClient, VALID_SCOPES, VALID_ACCESS_SCOPES, VALID_REPORT_EVENTS


class TestToolClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.lab.tools.test_clients.TestToolClient
    """

    def setUp(self):
        self.tool_client = ToolClient()
        self.mock_api_service = MagicMock()
        self.tool_client.api_service = self.mock_api_service
        self.project_id = "project-123"

    def test_create_tool_success(self):
        name = "TestTool"
        description = "A test tool"
        scope = "builtin"
        access_scope = "private"
        public_name = "test-tool"
        icon = "http://example.com/icon.png"
        open_api = "http://example.com/api"
        open_api_json = {"info": {"title": "Test API"}}
        report_events = "All"
        parameters = [{"key": "param1", "dataType": "String", "description": "Param 1", "isRequired": True}]
        automatic_publish = True
        expected_response = {"id": "tool-123", "name": name}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.create_tool(
            project_id=self.project_id,
            name=name,
            description=description,
            scope=scope,
            access_scope=access_scope,
            public_name=public_name,
            icon=icon,
            open_api=open_api,
            open_api_json=open_api_json,
            report_events=report_events,
            parameters=parameters,
            automatic_publish=automatic_publish
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.post.assert_called_once()
        call_args = self.mock_api_service.post.call_args
        data = call_args[1]['data']['tool']
        self.assertEqual(data['name'], name)
        self.assertEqual(data['description'], description)
        self.assertEqual(data['scope'], scope)
        self.assertEqual(data['accessScope'], access_scope)
        self.assertEqual(data['publicName'], public_name)
        self.assertEqual(data['icon'], icon)
        self.assertEqual(data['openApi'], open_api)
        self.assertIsInstance(data['openApiJson'], str)
        self.assertEqual(data['reportEvents'], report_events)
        self.assertEqual(data['parameters'], parameters)
        self.assertIn("automaticPublish=true", call_args[1]['endpoint'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_create_tool_invalid_scope(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.create_tool(
                project_id=self.project_id,
                name="TestTool",
                scope="invalid_scope"
            )
        self.assertEqual(str(context.exception), f"Scope must be one of {', '.join(VALID_SCOPES)}.")

    def test_create_tool_invalid_access_scope(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.create_tool(
                project_id=self.project_id,
                name="TestTool",
                access_scope="invalid_access"
            )
        self.assertEqual(str(context.exception), f"Access scope must be one of {', '.join(VALID_ACCESS_SCOPES)}.")

    def test_create_tool_invalid_report_events(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.create_tool(
                project_id=self.project_id,
                name="TestTool",
                report_events="invalid_event"
            )
        self.assertEqual(str(context.exception), f"Report events must be one of {', '.join(VALID_REPORT_EVENTS)}.")

    def test_list_tools_success(self):
        expected_response = {"tools": [{"id": "tool-1", "name": "Tool1"}]}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.list_tools(
            project_id=self.project_id,
            id="tool-1",
            count="50",
            access_scope="public",
            allow_drafts=True,
            scope="api",
            allow_external=True
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.get.assert_called_once()
        call_args = self.mock_api_service.get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['id'], "tool-1")
        self.assertEqual(params['count'], "50")
        self.assertEqual(params['accessScope'], "public")
        self.assertTrue(params['allowDrafts'])
        self.assertEqual(params['scope'], "api")
        self.assertTrue(params['allowExternal'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_list_tools_invalid_scope(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.list_tools(
                project_id=self.project_id,
                scope="invalid_scope"
            )
        self.assertEqual(str(context.exception), f"Scope must be one of {', '.join(VALID_SCOPES)}.")

    def test_get_tool_success(self):
        tool_id = "tool-123"
        expected_response = {"id": tool_id, "name": "TestTool"}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.get_tool(
            project_id=self.project_id,
            tool_id=tool_id,
            revision="1",
            version=0,
            allow_drafts=True
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.get.assert_called_once()
        call_args = self.mock_api_service.get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['revision'], "1")
        self.assertEqual(params['version'], 0)
        self.assertTrue(params['allowDrafts'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_delete_tool_success_with_id(self):
        tool_id = "tool-123"
        expected_response = {"status": "deleted"}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.delete.return_value = mock_response

        result = self.tool_client.delete_tool(
            project_id=self.project_id,
            tool_id=tool_id
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.delete.assert_called_once()
        headers = self.mock_api_service.delete.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_delete_tool_success_with_name(self):
        tool_name = "TestTool"
        expected_response = {"status": "deleted"}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.delete.return_value = mock_response

        result = self.tool_client.delete_tool(
            project_id=self.project_id,
            tool_name=tool_name
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.delete.assert_called_once()

    def test_delete_tool_invalid_input(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.delete_tool(project_id=self.project_id)
        self.assertEqual(str(context.exception), "Either tool_id or tool_name must be provided.")

    def test_update_tool_success(self):
        tool_id = "tool-123"
        name = "UpdatedTool"
        description = "Updated description"
        scope = "external"
        access_scope = "public"
        public_name = "updated-tool"
        icon = "http://example.com/new-icon.png"
        open_api = "http://example.com/new-api"
        open_api_json = {"info": {"title": "Updated API"}}
        report_events = "Start"
        parameters = [{"key": "param1", "dataType": "String", "description": "Param 1", "isRequired": True}]
        automatic_publish = True
        upsert = False
        expected_response = {"id": tool_id, "name": name}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.put.return_value = mock_response

        result = self.tool_client.update_tool(
            project_id=self.project_id,
            tool_id=tool_id,
            name=name,
            description=description,
            scope=scope,
            access_scope=access_scope,
            public_name=public_name,
            icon=icon,
            open_api=open_api,
            open_api_json=open_api_json,
            report_events=report_events,
            parameters=parameters,
            automatic_publish=automatic_publish,
            upsert=upsert
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.put.assert_called_once()
        call_args = self.mock_api_service.put.call_args
        data = call_args[1]['data']['tool']
        self.assertEqual(data['name'], name)
        self.assertEqual(data['description'], description)
        self.assertEqual(data['scope'], scope)
        self.assertEqual(data['accessScope'], access_scope)
        self.assertEqual(data['publicName'], public_name)
        self.assertEqual(data['icon'], icon)
        self.assertEqual(data['openApi'], open_api)
        self.assertIsInstance(data['openApiJson'], str)
        self.assertEqual(data['reportEvents'], report_events)
        self.assertEqual(data['parameters'], parameters)
        self.assertIn("automaticPublish=true", call_args[1]['endpoint'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_update_tool_invalid_scope(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.update_tool(
                project_id=self.project_id,
                tool_id="tool-123",
                scope="invalid_scope"
            )
        self.assertEqual(str(context.exception), f"Scope must be one of {', '.join(VALID_SCOPES)}.")

    def test_publish_tool_revision_success(self):
        tool_id = "tool-123"
        revision = "2"
        expected_response = {"status": "published"}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.publish_tool_revision(
            project_id=self.project_id,
            tool_id=tool_id,
            revision=revision
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.post.assert_called_once()
        call_args = self.mock_api_service.post.call_args
        data = call_args[1]['data']
        self.assertEqual(data['revision'], revision)
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_get_parameter_success_with_id(self):
        tool_id = "tool-123"
        expected_response = {"parameters": [{"key": "param1"}]}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.get_parameter(
            project_id=self.project_id,
            tool_id=tool_id,
            revision="1",
            version=0,
            allow_drafts=True
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.get.assert_called_once()
        call_args = self.mock_api_service.get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['revision'], "1")
        self.assertEqual(params['version'], 0)
        self.assertTrue(params['allowDrafts'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_get_parameter_success_with_public_name(self):
        tool_public_name = "test-tool"
        expected_response = {"parameters": [{"key": "param1"}]}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.get_parameter(
            project_id=self.project_id,
            tool_public_name=tool_public_name,
            revision="1",
            version=0,
            allow_drafts=True
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.get.assert_called_once()

    def test_get_parameter_invalid_input(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.get_parameter(project_id=self.project_id)
        self.assertEqual(str(context.exception), "Either tool_id or tool_public_name must be provided.")

    def test_set_parameter_success_with_id(self):
        tool_id = "tool-123"
        parameters = [{"key": "param1", "dataType": "String", "description": "Param 1", "isRequired": True}]
        expected_response = {"status": "updated"}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.set_parameter(
            project_id=self.project_id,
            tool_id=tool_id,
            parameters=parameters
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.post.assert_called_once()
        call_args = self.mock_api_service.post.call_args
        data = call_args[1]['data']['parameterDefinition']
        self.assertEqual(data['parameters'], parameters)
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_set_parameter_success_with_public_name(self):
        tool_public_name = "test-tool"
        parameters = [{"key": "param1", "dataType": "String", "description": "Param 1", "isRequired": True}]
        expected_response = {"status": "updated"}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.set_parameter(
            project_id=self.project_id,
            tool_public_name=tool_public_name,
            parameters=parameters
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.post.assert_called_once()

    def test_set_parameter_invalid_input(self):
        with self.assertRaises(ValueError) as context:
            self.tool_client.set_parameter(project_id=self.project_id, parameters=[{"key": "param1"}])
        self.assertEqual(str(context.exception), "Either tool_id or tool_public_name must be provided.")

        with self.assertRaises(ValueError) as context:
            self.tool_client.set_parameter(project_id=self.project_id, tool_id="tool-123", parameters=[])
        self.assertEqual(str(context.exception), "Parameters list must be provided and non-empty.")

    def test_create_tool_json_decode_error(self):
        name = "TestTool"
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.create_tool(
            project_id=self.project_id,
            name=name
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.post.assert_called_once()

    def test_list_tools_json_decode_error(self):
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.list_tools(
            project_id=self.project_id,
            scope="api"
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.get.assert_called_once()

    def test_get_tool_json_decode_error(self):
        tool_id = "tool-123"
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.get_tool(
            project_id=self.project_id,
            tool_id=tool_id
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.get.assert_called_once()

    def test_delete_tool_json_decode_error(self):
        tool_id = "tool-123"
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.delete.return_value = mock_response

        result = self.tool_client.delete_tool(
            project_id=self.project_id,
            tool_id=tool_id
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.delete.assert_called_once()

    def test_update_tool_json_decode_error(self):
        tool_id = "tool-123"
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.put.return_value = mock_response

        result = self.tool_client.update_tool(
            project_id=self.project_id,
            tool_id=tool_id,
            name="UpdatedTool"
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.put.assert_called_once()

    def test_publish_tool_revision_json_decode_error(self):
        tool_id = "tool-123"
        revision = "2"
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.publish_tool_revision(
            project_id=self.project_id,
            tool_id=tool_id,
            revision=revision
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.post.assert_called_once()

    def test_get_parameter_json_decode_error(self):
        tool_id = "tool-123"
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.get.return_value = mock_response

        result = self.tool_client.get_parameter(
            project_id=self.project_id,
            tool_id=tool_id
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.get.assert_called_once()

    def test_set_parameter_json_decode_error(self):
        tool_id = "tool-123"
        parameters = [{"key": "param1", "dataType": "String", "description": "Param 1", "isRequired": True}]
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "error text"
        self.mock_api_service.post.return_value = mock_response

        result = self.tool_client.set_parameter(
            project_id=self.project_id,
            tool_id=tool_id,
            parameters=parameters
        )

        self.assertEqual(result, "error text")
        self.mock_api_service.post.assert_called_once()

    def test_update_tool_with_upsert(self):
        tool_id = "tool-123"
        name = "UpsertedTool"
        expected_response = {"id": tool_id, "name": name}
        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        self.mock_api_service.put.return_value = mock_response

        result = self.tool_client.update_tool(
            project_id=self.project_id,
            tool_id=tool_id,
            name=name,
            upsert=True
        )

        self.assertEqual(result, expected_response)
        self.mock_api_service.put.assert_called_once()
        call_args = self.mock_api_service.put.call_args
        endpoint = call_args[1]['endpoint']
        self.assertIn("upsert", endpoint)

