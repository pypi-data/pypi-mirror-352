from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pygeai.core.base.mappers import ModelMapper, ErrorMapper
from pygeai.core.models import UsageLimit
from pygeai.organization.limits.managers import UsageLimitManager


class TestUsageLimitManager(TestCase):
    """
    python -m unittest pygeai.tests.organization.limits.test_managers.TestUsageLimitManager
    """

    def setUp(self):
        self.mock_client = MagicMock()
        self.manager = UsageLimitManager(organization_id="4aa15b61-d3c7-4a5c-99b8-052d18a04ff2")
        self.manager._UsageLimitManager__client = self.mock_client

        self.usage_limit_data = {
            "id": "4bb78b5a-07ea-4d15-84d6-e0baee53ff61",
            "hardLimit": 2000.0,
            "softLimit": 1000.0,
            "renewalStatus": "Renewable",
        }
        self.usage_limit = UsageLimit(
            id="4bb78b5a-07ea-4d15-84d6-e0baee53ff61",
            hard_limit=2000.0,
            related_entity_name="Pia.Data.Organization",
            remaining_usage=2000.0,
            renewal_status="Renewable",
            soft_limit=1000.0,
            status=1,
            subscription_type="Monthly",
            usage_unit="Cost",
            used_amount=0.0,
            valid_from=datetime(2025, 2, 20, 19, 33, 0),
            valid_until=datetime(2025, 3, 1, 0, 0, 0)
        )
        self.project_id = "1956c032-3c66-4435-acb8-6a06e52f819f"
        self.error_response = {"errors": [{"code": "400", "message": "Invalid request"}]}

    def test_set_organization_usage_limit(self):
        """Test setting an organization usage limit"""
        self.mock_client.set_organization_usage_limit.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.set_organization_usage_limit(self.usage_limit)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.set_organization_usage_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            usage_limit=self.usage_limit.to_dict()
        )

    def test_get_latest_usage_limit_from_organization(self):
        """Test retrieving the latest usage limit for an organization"""
        self.mock_client.get_organization_latest_usage_limit.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.get_latest_usage_limit_from_organization()

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.get_organization_latest_usage_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id
        )

    def test_update_organization_usage_limit(self):
        """Test updating an organization's usage limit"""
        self.mock_client.set_organization_hard_limit.return_value = self.usage_limit.to_dict()
        self.mock_client.set_organization_soft_limit.return_value = self.usage_limit.to_dict()
        self.mock_client.set_organization_renewal_status.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.update_organization_usage_limit(self.usage_limit)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.set_organization_hard_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            limit_id=self.usage_limit.id,
            hard_limit=self.usage_limit.hard_limit
        )
        self.mock_client.set_organization_soft_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            limit_id=self.usage_limit.id,
            soft_limit=self.usage_limit.soft_limit
        )
        self.mock_client.set_organization_renewal_status.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            limit_id=self.usage_limit.id,
            renewal_status=self.usage_limit.renewal_status
        )

    def test_delete_usage_limit_from_organization(self):
        """Test deleting an organization usage limit"""
        self.mock_client.delete_usage_limit_from_organization.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.delete_usage_limit_from_organization(self.usage_limit.id)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.delete_usage_limit_from_organization.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            limit_id=self.usage_limit.id
        )

    def test_set_project_usage_limit(self):
        """Test setting a project usage limit"""
        self.mock_client.set_project_usage_limit.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.set_project_usage_limit(self.project_id, self.usage_limit)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.set_project_usage_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id,
            usage_limit=self.usage_limit.to_dict()
        )

    def test_get_latest_usage_limit_from_project(self):
        """Test retrieving the latest usage limit for a project"""
        self.mock_client.get_latest_usage_limit_from_project.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.get_latest_usage_limit_from_project(self.project_id)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.get_latest_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id
        )

    def test_update_project_usage_limit(self):
        """Test updating a project's usage limit"""
        usage_limit_data = self.usage_limit.to_dict()
        self.mock_client.set_hard_limit_for_active_usage_limit_from_project.return_value = usage_limit_data
        self.mock_client.set_soft_limit_for_active_usage_limit_from_project.return_value = usage_limit_data
        self.mock_client.set_project_renewal_status.return_value = usage_limit_data

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.update_project_usage_limit(self.project_id, self.usage_limit)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.set_hard_limit_for_active_usage_limit_from_project.assert_called_once()
        self.mock_client.set_soft_limit_for_active_usage_limit_from_project.assert_called_once()
        self.mock_client.set_project_renewal_status.assert_called_once()

    def test_delete_usage_limit_from_project(self):
        """Test deleting a project usage limit"""
        self.mock_client.delete_usage_limit_from_project.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.delete_usage_limit_from_project(self.project_id, self.usage_limit)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.delete_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id,
            limit_id=self.usage_limit.id
        )

    def test_set_organization_usage_limit_error(self):
        """Test error handling when setting an organization usage limit"""
        self.mock_client.set_organization_usage_limit.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.set_organization_usage_limit(self.usage_limit)

        self.assertEqual(result, error_result)
        self.mock_client.set_organization_usage_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            usage_limit=self.usage_limit.to_dict()
        )

    def test_get_latest_usage_limit_from_organization_error(self):
        """Test error handling when retrieving the latest organization usage limit"""
        self.mock_client.get_organization_latest_usage_limit.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.get_latest_usage_limit_from_organization()

        self.assertEqual(result, error_result)
        self.mock_client.get_organization_latest_usage_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id
        )

    def test_get_all_usage_limits_from_organization_success(self):
        """Test retrieving all usage limits for an organization"""
        response_data = {"limits": [self.usage_limit.to_dict()]}
        self.mock_client.get_all_usage_limits_from_organization.return_value = response_data
        usage_limit_list = [self.usage_limit]

        with patch.object(ModelMapper, 'map_to_usage_limit_list', return_value=usage_limit_list):
            result = self.manager.get_all_usage_limits_from_organization()

        self.assertEqual(result, usage_limit_list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.usage_limit.id)
        self.mock_client.get_all_usage_limits_from_organization.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id
        )

    def test_get_all_usage_limits_from_organization_error(self):
        """Test error handling when retrieving all organization usage limits"""
        self.mock_client.get_all_usage_limits_from_organization.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.get_all_usage_limits_from_organization()

        self.assertEqual(result, error_result)
        self.mock_client.get_all_usage_limits_from_organization.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id
        )

    def test_delete_usage_limit_from_organization_error(self):
        """Test error handling when deleting an organization usage limit"""
        self.mock_client.delete_usage_limit_from_organization.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.delete_usage_limit_from_organization(self.usage_limit.id)

        self.assertEqual(result, error_result)
        self.mock_client.delete_usage_limit_from_organization.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            limit_id=self.usage_limit.id
        )

    def test_set_project_usage_limit_error(self):
        """Test error handling when setting a project usage limit"""
        self.mock_client.set_project_usage_limit.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.set_project_usage_limit(self.project_id, self.usage_limit)

        self.assertEqual(result, error_result)
        self.mock_client.set_project_usage_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id,
            usage_limit=self.usage_limit.to_dict()
        )

    def test_get_all_usage_limits_from_project_success(self):
        """Test retrieving all usage limits for a project"""
        response_data = {"limits": [self.usage_limit.to_dict()]}
        self.mock_client.get_all_usage_limits_from_project.return_value = response_data
        usage_limit_list = [self.usage_limit]

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=usage_limit_list):
            result = self.manager.get_all_usage_limits_from_project(self.project_id)

        self.assertEqual(result, usage_limit_list)
        self.mock_client.get_all_usage_limits_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id
        )

    def test_get_all_usage_limits_from_project_error(self):
        """Test error handling when retrieving all project usage limits"""
        self.mock_client.get_all_usage_limits_from_project.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.get_all_usage_limits_from_project(self.project_id)

        self.assertEqual(result, error_result)
        self.mock_client.get_all_usage_limits_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id
        )

    def test_get_latest_usage_limit_from_project_error(self):
        """Test error handling when retrieving the latest project usage limit"""
        self.mock_client.get_latest_usage_limit_from_project.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.get_latest_usage_limit_from_project(self.project_id)

        self.assertEqual(result, error_result)
        self.mock_client.get_latest_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id
        )

    def test_get_active_usage_limit_from_project_success(self):
        """Test retrieving the active usage limit for a project"""
        self.mock_client.get_active_usage_limit_from_project.return_value = self.usage_limit.to_dict()

        with patch.object(ModelMapper, 'map_to_usage_limit', return_value=self.usage_limit):
            result = self.manager.get_active_usage_limit_from_project(self.project_id)

        self.assertEqual(result.id, self.usage_limit.id)
        self.mock_client.get_active_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id
        )

    def test_get_active_usage_limit_from_project_error(self):
        """Test error handling when retrieving the active project usage limit"""
        self.mock_client.get_active_usage_limit_from_project.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.get_active_usage_limit_from_project(self.project_id)

        self.assertEqual(result, error_result)
        self.mock_client.get_active_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id
        )

    def test_delete_usage_limit_from_project_error(self):
        """Test error handling when deleting a project usage limit"""
        self.mock_client.delete_usage_limit_from_project.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result):
            result = self.manager.delete_usage_limit_from_project(self.project_id, self.usage_limit)

        self.assertEqual(result, error_result)
        self.mock_client.delete_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id,
            limit_id=self.usage_limit.id
        )

    def test_update_organization_usage_limit_error(self):
        """Test error handling when updating an organization usage limit"""
        # Use a usage_limit with only hard_limit to isolate the error response
        error_usage_limit = UsageLimit(
            id=self.usage_limit.id,
            hard_limit=2000.0,
            related_entity_name="Pia.Data.Organization",
            status=1,
            subscription_type="Monthly",
            usage_unit="Cost",
            valid_from=datetime(2025, 2, 20, 19, 33, 0),
            valid_until=datetime(2025, 3, 1, 0, 0, 0)
        )
        self.mock_client.set_organization_hard_limit.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result) as mock_error_mapper:
            with patch.object(ModelMapper, 'map_to_usage_limit') as mock_usage_limit_mapper:
                result = self.manager.update_organization_usage_limit(error_usage_limit)

        self.assertEqual(result, error_result)
        self.mock_client.set_organization_hard_limit.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            limit_id=error_usage_limit.id,
            hard_limit=error_usage_limit.hard_limit
        )
        mock_error_mapper.assert_called_once_with(self.error_response)
        mock_usage_limit_mapper.assert_not_called()

    def test_update_project_usage_limit_error(self):
        """Test error handling when updating a project usage limit"""
        # Use a usage_limit with only hard_limit to isolate the error response
        error_usage_limit = UsageLimit(
            id=self.usage_limit.id,
            hard_limit=2000.0,
            related_entity_name="Pia.Data.Organization",
            status=1,
            subscription_type="Monthly",
            usage_unit="Cost",
            valid_from=datetime(2025, 2, 20, 19, 33, 0),
            valid_until=datetime(2025, 3, 1, 0, 0, 0)
        )
        self.mock_client.set_hard_limit_for_active_usage_limit_from_project.return_value = self.error_response
        error_result = MagicMock()

        with patch.object(ErrorMapper, 'map_to_error_list_response', return_value=error_result) as mock_error_mapper:
            with patch.object(ModelMapper, 'map_to_usage_limit') as mock_usage_limit_mapper:
                result = self.manager.update_project_usage_limit(self.project_id, error_usage_limit)

        self.assertEqual(result, error_result)
        self.mock_client.set_hard_limit_for_active_usage_limit_from_project.assert_called_once_with(
            organization=self.manager._UsageLimitManager__organization_id,
            project=self.project_id,
            limit_id=error_usage_limit.id,
            hard_limit=error_usage_limit.hard_limit
        )
        mock_error_mapper.assert_called_once_with(self.error_response)
        mock_usage_limit_mapper.assert_not_called()