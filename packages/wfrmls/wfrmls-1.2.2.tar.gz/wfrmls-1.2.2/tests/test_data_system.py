"""Tests for WFRMLS Data System module."""

import pytest
from datetime import datetime, date
from typing import Dict, Any
from unittest.mock import Mock, patch

from wfrmls.data_system import DataSystemClient
from wfrmls.exceptions import WFRMLSError


class TestDataSystemClient:
    """Test suite for DataSystemClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = DataSystemClient(bearer_token="test_token")

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_systems_basic(self, mock_get: Mock) -> None:
        """Test basic get_data_systems functionality."""
        mock_response: Dict[str, Any] = {
            "value": [
                {
                    "DataSystemKey": "WFRMLS",
                    "DataSystemName": "WFRMLS",
                    "DataSystemStatus": "Active"
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_data_systems()

        mock_get.assert_called_once_with("DataSystem", params={})
        assert result == mock_response

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_systems_with_all_params(self, mock_get: Mock) -> None:
        """Test get_data_systems with all parameters."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get.return_value = mock_response

        result = self.client.get_data_systems(
            top=50,
            skip=10,
            filter_query="DataSystemStatus eq 'Active'",
            select=["DataSystemKey", "DataSystemName"],
            orderby="DataSystemName asc",
            expand=["Resources"],
            count=True
        )

        expected_params = {
            "$top": 50,
            "$skip": 10,
            "$filter": "DataSystemStatus eq 'Active'",
            "$select": "DataSystemKey,DataSystemName",
            "$orderby": "DataSystemName asc",
            "$expand": "Resources",
            "$count": "true"
        }

        mock_get.assert_called_once_with("DataSystem", params=expected_params)

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_systems_top_limit_enforcement(self, mock_get: Mock) -> None:
        """Test that top parameter is limited to 200."""
        mock_get.return_value = {"value": []}

        self.client.get_data_systems(top=300)

        expected_params = {"$top": 200}
        mock_get.assert_called_once_with("DataSystem", params=expected_params)

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_systems_select_string(self, mock_get: Mock) -> None:
        """Test get_data_systems with select as string."""
        mock_get.return_value = {"value": []}

        self.client.get_data_systems(select="DataSystemKey,DataSystemName")

        expected_params = {"$select": "DataSystemKey,DataSystemName"}
        mock_get.assert_called_once_with("DataSystem", params=expected_params)

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_systems_expand_string(self, mock_get: Mock) -> None:
        """Test get_data_systems with expand as string."""
        mock_get.return_value = {"value": []}

        self.client.get_data_systems(expand="Resources,Metadata")

        expected_params = {"$expand": "Resources,Metadata"}
        mock_get.assert_called_once_with("DataSystem", params=expected_params)

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_systems_count_false(self, mock_get: Mock) -> None:
        """Test get_data_systems with count=False."""
        mock_get.return_value = {"value": []}

        self.client.get_data_systems(count=False)

        expected_params = {"$count": "false"}
        mock_get.assert_called_once_with("DataSystem", params=expected_params)

    @patch("wfrmls.data_system.DataSystemClient.get")
    def test_get_data_system(self, mock_get: Mock) -> None:
        """Test get_data_system functionality."""
        data_system_key = "WFRMLS"
        mock_response: Dict[str, Any] = {
            "DataSystemKey": data_system_key,
            "DataSystemName": "WFRMLS",
            "DataSystemStatus": "Active"
        }
        mock_get.return_value = mock_response

        result = self.client.get_data_system(data_system_key)

        mock_get.assert_called_once_with(f"DataSystem('{data_system_key}')")
        assert result == mock_response

    @patch("wfrmls.data_system.DataSystemClient.get_data_systems")
    def test_get_system_info(self, mock_get_data_systems: Mock) -> None:
        """Test get_system_info functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_data_systems.return_value = mock_response

        result = self.client.get_system_info()

        mock_get_data_systems.assert_called_once_with(top=10)

    @patch("wfrmls.data_system.DataSystemClient.get_data_systems")
    def test_get_modified_data_systems_datetime(self, mock_get_data_systems: Mock) -> None:
        """Test get_modified_data_systems with datetime object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_data_systems.return_value = mock_response

        since_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = self.client.get_modified_data_systems(
            since=since_datetime,
            orderby="ModificationTimestamp desc"
        )

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_data_systems.assert_called_once_with(
            filter_query=expected_filter,
            orderby="ModificationTimestamp desc"
        )

    @patch("wfrmls.data_system.DataSystemClient.get_data_systems")
    def test_get_modified_data_systems_date(self, mock_get_data_systems: Mock) -> None:
        """Test get_modified_data_systems with date object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_data_systems.return_value = mock_response

        since_date = date(2024, 1, 1)
        result = self.client.get_modified_data_systems(since=since_date)

        expected_filter = "ModificationTimestamp gt '2024-01-01T00:00:00Z'"
        mock_get_data_systems.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.data_system.DataSystemClient.get_data_systems")
    def test_get_modified_data_systems_string(self, mock_get_data_systems: Mock) -> None:
        """Test get_modified_data_systems with string."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_data_systems.return_value = mock_response

        since_string = "2024-01-01T12:00:00Z"
        result = self.client.get_modified_data_systems(since=since_string)

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_data_systems.assert_called_once_with(filter_query=expected_filter)

    def test_init_default_params(self) -> None:
        """Test DataSystemClient initialization with default parameters."""
        client = DataSystemClient()
        # Test that it doesn't raise an exception and creates properly
        assert hasattr(client, 'bearer_token')
        assert hasattr(client, 'base_url')

    def test_init_with_params(self) -> None:
        """Test DataSystemClient initialization with custom parameters."""
        client = DataSystemClient(
            bearer_token="custom_token",
            base_url="https://custom.api.com"
        )
        assert hasattr(client, 'bearer_token')
        assert hasattr(client, 'base_url') 