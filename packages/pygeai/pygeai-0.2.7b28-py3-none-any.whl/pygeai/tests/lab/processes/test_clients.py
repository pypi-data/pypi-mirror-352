import unittest
from unittest.mock import MagicMock
from json import JSONDecodeError
from pygeai.lab.processes.clients import AgenticProcessClient


class TestAgenticProcessClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.lab.processes.test_clients.TestAgenticProcessClient
    """

    def setUp(self):
        self.client = AgenticProcessClient()
        self.client.api_service = MagicMock()
        self.project_id = "test-project-id"
        self.process_id = "test-process-id"
        self.process_name = "test-process-name"
        self.task_id = "test-task-id"
        self.instance_id = "test-instance-id"
        self.thread_id = "test-thread-id"
        self.kb_id = "test-kb-id"
        self.revision = "1"
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"status": "success"}
        self.mock_response.text = "success text"

    def test_create_process_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_process(
            project_id=self.project_id,
            key="test-key",
            name="Test Process",
            description="Test Description",
            automatic_publish=True
        )

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_create_process_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_process(
            project_id=self.project_id,
            key="test-key",
            name="Test Process"
        )

        self.assertEqual(result, "success text")

    def test_update_process_missing_identifier(self):
        with self.assertRaises(ValueError) as context:
            self.client.update_process(project_id=self.project_id)

        self.assertEqual(str(context.exception), "Either process_id or name must be provided.")

    def test_update_process_success_with_id(self):
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_process(
            project_id=self.project_id,
            process_id=self.process_id,
            name="Updated Process",
            automatic_publish=True
        )

        self.client.api_service.put.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_get_process_missing_identifier(self):
        with self.assertRaises(ValueError) as context:
            self.client.get_process(project_id=self.project_id)

        self.assertEqual(str(context.exception), "Either process_id or process_name must be provided.")

    def test_get_process_success_with_id(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_process(
            project_id=self.project_id,
            process_id=self.process_id,
            revision="0"
        )

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_list_processes_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.list_processes(
            project_id=self.project_id,
            name="Test Process",
            allow_draft=True
        )

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_list_process_instances_missing_process_id(self):
        with self.assertRaises(ValueError) as context:
            self.client.list_process_instances(project_id=self.project_id, process_id="")

        self.assertEqual(str(context.exception), "Process ID must be provided.")

    def test_delete_process_missing_identifier(self):
        with self.assertRaises(ValueError) as context:
            self.client.delete_process(project_id=self.project_id)

        self.assertEqual(str(context.exception), "Either process_id or process_name must be provided.")

    def test_publish_process_revision_missing_revision(self):
        with self.assertRaises(ValueError) as context:
            self.client.publish_process_revision(
                project_id=self.project_id,
                process_id=self.process_id
            )

        self.assertEqual(str(context.exception), "Revision must be provided.")

    def test_create_task_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_task(
            project_id=self.project_id,
            name="Test Task",
            description="Task Description"
        )

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_get_task_missing_identifier(self):
        with self.assertRaises(ValueError) as context:
            self.client.get_task(project_id=self.project_id, task_id="", task_name="")

        self.assertEqual(str(context.exception), "Either task_id or task_name must be provided.")

    def test_start_instance_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.start_instance(
            project_id=self.project_id,
            process_name=self.process_name,
            subject="Test Subject"
        )

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_abort_instance_missing_id(self):
        with self.assertRaises(ValueError) as context:
            self.client.abort_instance(project_id=self.project_id, instance_id="")

        self.assertEqual(str(context.exception), "Instance ID must be provided.")

    def test_send_user_signal_missing_signal_name(self):
        with self.assertRaises(ValueError) as context:
            self.client.send_user_signal(
                project_id=self.project_id,
                instance_id=self.instance_id,
                signal_name=""
            )

        self.assertEqual(str(context.exception), "Signal name must be provided.")

    def test_create_kb_success(self):
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_kb(
            project_id=self.project_id,
            name="Test KB",
            artifacts=["artifact1"]
        )

        self.client.api_service.post.assert_called_once()
        self.assertEqual(result, {"status": "success"})

    def test_list_jobs_success(self):
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.list_jobs(
            project_id=self.project_id,
            topic="test-topic"
        )

        self.client.api_service.get.assert_called_once()
        self.assertEqual(result, {"status": "success"})

