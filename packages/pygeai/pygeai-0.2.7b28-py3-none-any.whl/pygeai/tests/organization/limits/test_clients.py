from unittest import TestCase
from unittest.mock import MagicMock
import json
from pydantic import ValidationError

from pygeai.core.models import UsageLimit
from pygeai.organization.limits.clients import UsageLimitClient


class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = json.dumps(content).encode('utf-8') if isinstance(content, dict) else content
        self.status_code = status_code


class TestUsageLimitClient(TestCase):
    """
    python -m unittest pygeai.tests.organization.limits.test_clients.TestUsageLimitClient
    """

    def setUp(self):
        self.client = UsageLimitClient()
        self.client.api_service = MagicMock()
        self.organization = "org-123"
        self.project = "proj-456"
        self.limit_id = "limit-789"
        self.valid_usage_limit = {
            "subscriptionType": "Monthly",
            "usageUnit": "Requests",
            "softLimit": 1000.0,
            "hardLimit": 2000.0,
            "renewalStatus": "Renewable"
        }
        self.valid_response = {
            "id": self.limit_id,
            "subscriptionType": "Monthly",
            "usageUnit": "Requests",
            "softLimit": 1000.0,
            "hardLimit": 2000.0,
            "renewalStatus": "Renewable",
            "status": 1,
            "validFrom": "2025-05-28T12:00:00Z",
            "validUntil": "2025-06-28T12:00:00Z"
        }

    def test_set_organization_usage_limit_success(self):
        self.client.api_service.post.return_value = MockResponse(self.valid_response)
        result = self.client.set_organization_usage_limit(self.organization, self.valid_usage_limit)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits"
        self.client.api_service.post.assert_called_once_with(endpoint=expected_endpoint, data=self.valid_usage_limit)
        self.assertEqual(result, self.valid_response)
        UsageLimit.model_validate(result)

    def test_set_organization_usage_limit_invalid_json(self):
        self.client.api_service.post.return_value = MockResponse("invalid json", status_code=200)
        with self.assertRaises(json.JSONDecodeError):
            self.client.set_organization_usage_limit(self.organization, self.valid_usage_limit)

    def test_set_organization_usage_limit_invalid_usage_limit(self):
        invalid_usage_limit = self.valid_usage_limit.copy()
        invalid_usage_limit["renewalStatus"] = "InvalidStatus"
        self.client.api_service.post.return_value = MockResponse({"error": "Invalid renewal status"}, status_code=400)
        result = self.client.set_organization_usage_limit(self.organization, invalid_usage_limit)
        self.assertEqual(result, {"error": "Invalid renewal status"})
        with self.assertRaises(ValidationError):
            UsageLimit.model_validate(invalid_usage_limit)

    def test_get_organization_latest_usage_limit_success(self):
        self.client.api_service.get.return_value = MockResponse(self.valid_response)
        result = self.client.get_organization_latest_usage_limit(self.organization)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits/latest"
        self.client.api_service.get.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, self.valid_response)
        UsageLimit.model_validate(result)

    def test_get_organization_latest_usage_limit_invalid_json(self):
        self.client.api_service.get.return_value = MockResponse("invalid json", status_code=200)
        with self.assertRaises(json.JSONDecodeError):
            self.client.get_organization_latest_usage_limit(self.organization)

    def test_get_all_usage_limits_from_organization_success(self):
        response = {"limits": [self.valid_response]}
        self.client.api_service.get.return_value = MockResponse(response)
        result = self.client.get_all_usage_limits_from_organization(self.organization)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits"
        self.client.api_service.get.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, response)
        for limit in result["limits"]:
            UsageLimit.model_validate(limit)

    def test_delete_usage_limit_from_organization_success(self):
        response = {"status": "deleted"}
        self.client.api_service.delete.return_value = MockResponse(response)
        result = self.client.delete_usage_limit_from_organization(self.organization, self.limit_id)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits/{self.limit_id}"
        self.client.api_service.delete.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, response)

    def test_set_organization_hard_limit_success(self):
        hard_limit = 3000.0
        response = self.valid_response.copy()
        response["hardLimit"] = hard_limit
        self.client.api_service.put.return_value = MockResponse(response)
        result = self.client.set_organization_hard_limit(self.organization, self.limit_id, hard_limit)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits/{self.limit_id}/hardLimit"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"hardLimit": hard_limit})
        self.assertEqual(result, response)
        UsageLimit.model_validate(result)

    def test_set_organization_soft_limit_success(self):
        soft_limit = 1500.0
        response = self.valid_response.copy()
        response["softLimit"] = soft_limit
        self.client.api_service.put.return_value = MockResponse(response)
        result = self.client.set_organization_soft_limit(self.organization, self.limit_id, soft_limit)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits/{self.limit_id}/softLimit"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"softLimit": soft_limit})
        self.assertEqual(result, response)
        UsageLimit.model_validate(result)

    def test_set_organization_renewal_status_success(self):
        renewal_status = "NonRenewable"
        response = self.valid_response.copy()
        response["renewalStatus"] = renewal_status
        self.client.api_service.put.return_value = MockResponse(response)
        result = self.client.set_organization_renewal_status(self.organization, self.limit_id, renewal_status)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits/{self.limit_id}/renewalStatus"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"renewalStatus": renewal_status})
        self.assertEqual(result, response)
        UsageLimit.model_validate(result)

    def test_set_organization_renewal_status_invalid(self):
        invalid_status = "InvalidStatus"
        self.client.api_service.put.return_value = MockResponse({"error": "Invalid renewal status"}, status_code=400)
        result = self.client.set_organization_renewal_status(self.organization, self.limit_id, invalid_status)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/limits/{self.limit_id}/renewalStatus"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"renewalStatus": invalid_status})
        self.assertEqual(result, {"error": "Invalid renewal status"})

    def test_set_project_usage_limit_success(self):
        self.client.api_service.post.return_value = MockResponse(self.valid_response)
        result = self.client.set_project_usage_limit(self.organization, self.project, self.valid_usage_limit)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits"
        self.client.api_service.post.assert_called_once_with(endpoint=expected_endpoint, data=self.valid_usage_limit)
        self.assertEqual(result, self.valid_response)
        UsageLimit.model_validate(result)

    def test_set_project_usage_limit_invalid_usage_limit(self):
        invalid_usage_limit = self.valid_usage_limit.copy()
        invalid_usage_limit["subscriptionType"] = "InvalidType"
        self.client.api_service.post.return_value = MockResponse({"error": "Invalid subscription type"}, status_code=400)
        result = self.client.set_project_usage_limit(self.organization, self.project, invalid_usage_limit)
        self.assertEqual(result, {"error": "Invalid subscription type"})
        with self.assertRaises(ValidationError):
            UsageLimit.model_validate(invalid_usage_limit)

    def test_get_all_usage_limits_from_project_success(self):
        response = {"limits": [self.valid_response]}
        self.client.api_service.get.return_value = MockResponse(response)
        result = self.client.get_all_usage_limits_from_project(self.organization, self.project)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits"
        self.client.api_service.get.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, response)
        for limit in result["limits"]:
            UsageLimit.model_validate(limit)

    def test_get_latest_usage_limit_from_project_success(self):
        self.client.api_service.get.return_value = MockResponse(self.valid_response)
        result = self.client.get_latest_usage_limit_from_project(self.organization, self.project)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits/latest"
        self.client.api_service.get.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, self.valid_response)
        UsageLimit.model_validate(result)

    def test_get_active_usage_limit_from_project_success(self):
        self.client.api_service.get.return_value = MockResponse(self.valid_response)
        result = self.client.get_active_usage_limit_from_project(self.organization, self.project)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits/active"
        self.client.api_service.get.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, self.valid_response)
        UsageLimit.model_validate(result)

    def test_delete_usage_limit_from_project_success(self):
        response = {"status": "deleted"}
        self.client.api_service.delete.return_value = MockResponse(response)
        result = self.client.delete_usage_limit_from_project(self.organization, self.project, self.limit_id)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits/{self.limit_id}"
        self.client.api_service.delete.assert_called_once_with(endpoint=expected_endpoint)
        self.assertEqual(result, response)

    def test_set_hard_limit_for_active_usage_limit_from_project_success(self):
        hard_limit = 4000.0
        response = self.valid_response.copy()
        response["hardLimit"] = hard_limit
        self.client.api_service.put.return_value = MockResponse(response)
        result = self.client.set_hard_limit_for_active_usage_limit_from_project(
            self.organization, self.project, self.limit_id, hard_limit
        )
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits/{self.limit_id}/hardLimit"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"hardLimit": hard_limit})
        self.assertEqual(result, response)
        UsageLimit.model_validate(result)

    def test_set_soft_limit_for_active_usage_limit_from_project_success(self):
        soft_limit = 2000.0
        response = self.valid_response.copy()
        response["softLimit"] = soft_limit
        self.client.api_service.put.return_value = MockResponse(response)
        result = self.client.set_soft_limit_for_active_usage_limit_from_project(self.organization, self.project, self.limit_id, soft_limit)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits/{self.limit_id}/softLimit"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"softLimit": soft_limit})
        self.assertEqual(result, response)
        UsageLimit.model_validate(result)

    def test_set_project_renewal_status_success(self):
        renewal_status = "Renewable"
        response = self.valid_response.copy()
        response["renewalStatus"] = renewal_status
        self.client.api_service.put.return_value = MockResponse(response)
        result = self.client.set_project_renewal_status(self.organization, self.project, self.limit_id, renewal_status)
        expected_endpoint = f"v2/usageLimits/organizations/{self.organization}/projects/{self.project}/limits/{self.limit_id}/renewalStatus"
        self.client.api_service.put.assert_called_once_with(endpoint=expected_endpoint, data={"renewalStatus": renewal_status})
        self.assertEqual(result, response)
        UsageLimit.model_validate(result)