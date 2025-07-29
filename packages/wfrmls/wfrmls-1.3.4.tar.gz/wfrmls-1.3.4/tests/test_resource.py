"""Tests for WFRMLS Resource module."""

from datetime import date, datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from wfrmls.exceptions import WFRMLSError
from wfrmls.resource import ResourceClient


class TestResourceClient:
    """Test suite for ResourceClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = ResourceClient(bearer_token="test_token")

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resources_basic(self, mock_get: Mock) -> None:
        """Test basic get_resources functionality."""
        mock_response: Dict[str, Any] = {
            "value": [
                {
                    "ResourceKey": "Property",
                    "ResourceName": "Property",
                    "StandardName": "Property",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_resources()

        mock_get.assert_called_once_with("Resource", params={})
        assert result == mock_response

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resources_with_all_params(self, mock_get: Mock) -> None:
        """Test get_resources with all parameters."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get.return_value = mock_response

        result = self.client.get_resources(
            top=50,
            skip=10,
            filter_query="StandardName ne null",
            select=["ResourceKey", "ResourceName"],
            orderby="ResourceName asc",
            expand=["Fields"],
            count=True,
        )

        expected_params = {
            "$top": 50,
            "$skip": 10,
            "$filter": "StandardName ne null",
            "$select": "ResourceKey,ResourceName",
            "$orderby": "ResourceName asc",
            "$expand": "Fields",
            "$count": "true",
        }

        mock_get.assert_called_once_with("Resource", params=expected_params)

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resources_top_limit_enforcement(self, mock_get: Mock) -> None:
        """Test that top parameter is limited to 200."""
        mock_get.return_value = {"value": []}

        self.client.get_resources(top=300)

        expected_params = {"$top": 200}
        mock_get.assert_called_once_with("Resource", params=expected_params)

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resources_select_string(self, mock_get: Mock) -> None:
        """Test get_resources with select as string."""
        mock_get.return_value = {"value": []}

        self.client.get_resources(select="ResourceKey,ResourceName")

        expected_params = {"$select": "ResourceKey,ResourceName"}
        mock_get.assert_called_once_with("Resource", params=expected_params)

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resources_expand_string(self, mock_get: Mock) -> None:
        """Test get_resources with expand as string."""
        mock_get.return_value = {"value": []}

        self.client.get_resources(expand="Fields,Metadata")

        expected_params = {"$expand": "Fields,Metadata"}
        mock_get.assert_called_once_with("Resource", params=expected_params)

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resources_count_false(self, mock_get: Mock) -> None:
        """Test get_resources with count=False."""
        mock_get.return_value = {"value": []}

        self.client.get_resources(count=False)

        expected_params = {"$count": "false"}
        mock_get.assert_called_once_with("Resource", params=expected_params)

    @patch("wfrmls.resource.ResourceClient.get")
    def test_get_resource(self, mock_get: Mock) -> None:
        """Test get_resource functionality."""
        resource_key = "Property"
        mock_response: Dict[str, Any] = {
            "ResourceKey": resource_key,
            "ResourceName": "Property",
            "StandardName": "Property",
        }
        mock_get.return_value = mock_response

        result = self.client.get_resource(resource_key)

        mock_get.assert_called_once_with(f"Resource('{resource_key}')")
        assert result == mock_response

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_resource_by_name(self, mock_get_resources: Mock) -> None:
        """Test get_resource_by_name functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        result = self.client.get_resource_by_name(
            resource_name="Property", expand="Fields"
        )

        mock_get_resources.assert_called_once_with(
            filter_query="ResourceName eq 'Property'", expand="Fields"
        )

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_resource_by_name_with_existing_filter(
        self, mock_get_resources: Mock
    ) -> None:
        """Test get_resource_by_name with existing filter_query."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        result = self.client.get_resource_by_name(
            resource_name="Member", filter_query="StandardName ne null"
        )

        expected_filter = "ResourceName eq 'Member' and StandardName ne null"
        mock_get_resources.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_standard_resources(self, mock_get_resources: Mock) -> None:
        """Test get_standard_resources functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        result = self.client.get_standard_resources()

        mock_get_resources.assert_called_once_with(filter_query="StandardName ne null")

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_standard_resources_with_existing_filter(
        self, mock_get_resources: Mock
    ) -> None:
        """Test get_standard_resources with existing filter_query."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        result = self.client.get_standard_resources(
            filter_query="ResourceName eq 'Property'"
        )

        expected_filter = "StandardName ne null and ResourceName eq 'Property'"
        mock_get_resources.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_resources_with_fields(self, mock_get_resources: Mock) -> None:
        """Test get_resources_with_fields functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        result = self.client.get_resources_with_fields(top=10)

        mock_get_resources.assert_called_once_with(expand="Fields", top=10)

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_modified_resources_datetime(self, mock_get_resources: Mock) -> None:
        """Test get_modified_resources with datetime object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        since_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = self.client.get_modified_resources(
            since=since_datetime, orderby="ModificationTimestamp desc"
        )

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_resources.assert_called_once_with(
            filter_query=expected_filter, orderby="ModificationTimestamp desc"
        )

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_modified_resources_date(self, mock_get_resources: Mock) -> None:
        """Test get_modified_resources with date object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        since_date = date(2024, 1, 1)
        result = self.client.get_modified_resources(since=since_date)

        expected_filter = "ModificationTimestamp gt '2024-01-01T00:00:00Z'"
        mock_get_resources.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.resource.ResourceClient.get_resources")
    def test_get_modified_resources_string(self, mock_get_resources: Mock) -> None:
        """Test get_modified_resources with string."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_resources.return_value = mock_response

        since_string = "2024-01-01T12:00:00Z"
        result = self.client.get_modified_resources(since=since_string)

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_resources.assert_called_once_with(filter_query=expected_filter)

    def test_init_default_params(self) -> None:
        """Test ResourceClient initialization with default parameters."""
        client = ResourceClient()
        # Test that it doesn't raise an exception and creates properly
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")

    def test_init_with_params(self) -> None:
        """Test ResourceClient initialization with custom parameters."""
        client = ResourceClient(
            bearer_token="custom_token", base_url="https://custom.api.com"
        )
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")
