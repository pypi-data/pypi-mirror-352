"""Tests for WFRMLS Property Unit Types module."""

from datetime import date, datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from wfrmls.exceptions import WFRMLSError
from wfrmls.property_unit_types import PropertyUnitTypesClient


class TestPropertyUnitTypesClient:
    """Test suite for PropertyUnitTypesClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = PropertyUnitTypesClient(bearer_token="test_token")

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_types_basic(self, mock_get: Mock) -> None:
        """Test basic get_property_unit_types functionality."""
        mock_response: Dict[str, Any] = {
            "value": [
                {
                    "PropertyUnitTypeKey": "PUT123",
                    "PropertyUnitTypeName": "Apartment",
                    "PropertyUnitTypeStatus": "Active",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_property_unit_types()

        mock_get.assert_called_once_with("PropertyUnitTypes", params={})
        assert result == mock_response

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_types_with_all_params(self, mock_get: Mock) -> None:
        """Test get_property_unit_types with all parameters."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get.return_value = mock_response

        result = self.client.get_property_unit_types(
            top=50,
            skip=10,
            filter_query="UnitType eq 'Condo'",
            select=["UnitTypeKey", "UnitType"],
            orderby="UnitType asc",
            expand=["Properties"],
            count=True,
        )

        expected_params = {
            "$top": 50,
            "$skip": 10,
            "$filter": "UnitType eq 'Condo'",
            "$select": "UnitTypeKey,UnitType",
            "$orderby": "UnitType asc",
            "$expand": "Properties",
            "$count": "true",
        }

        mock_get.assert_called_once_with("PropertyUnitTypes", params=expected_params)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_types_top_limit_enforcement(
        self, mock_get: Mock
    ) -> None:
        """Test that top parameter is limited to 200."""
        mock_get.return_value = {"value": []}

        self.client.get_property_unit_types(top=300)

        expected_params = {"$top": 200}
        mock_get.assert_called_once_with("PropertyUnitTypes", params=expected_params)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_types_select_string(self, mock_get: Mock) -> None:
        """Test get_property_unit_types with select as string."""
        mock_get.return_value = {"value": []}

        self.client.get_property_unit_types(select="UnitTypeKey,UnitType")

        expected_params = {"$select": "UnitTypeKey,UnitType"}
        mock_get.assert_called_once_with("PropertyUnitTypes", params=expected_params)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_types_expand_string(self, mock_get: Mock) -> None:
        """Test get_property_unit_types with expand as string."""
        mock_get.return_value = {"value": []}

        self.client.get_property_unit_types(expand="Properties,Resources")

        expected_params = {"$expand": "Properties,Resources"}
        mock_get.assert_called_once_with("PropertyUnitTypes", params=expected_params)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_types_count_false(self, mock_get: Mock) -> None:
        """Test get_property_unit_types with count=False."""
        mock_get.return_value = {"value": []}

        self.client.get_property_unit_types(count=False)

        expected_params = {"$count": "false"}
        mock_get.assert_called_once_with("PropertyUnitTypes", params=expected_params)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get")
    def test_get_property_unit_type(self, mock_get: Mock) -> None:
        """Test get_property_unit_type functionality."""
        unit_type_key = "CONDO"
        mock_response: Dict[str, Any] = {
            "UnitTypeKey": unit_type_key,
            "UnitType": "Condo",
            "Description": "Condominium unit",
        }
        mock_get.return_value = mock_response

        result = self.client.get_property_unit_type(unit_type_key)

        mock_get.assert_called_once_with(f"PropertyUnitTypes('{unit_type_key}')")
        assert result == mock_response

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_unit_types_for_property(self, mock_get_unit_types: Mock) -> None:
        """Test get_unit_types_for_property functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        result = self.client.get_unit_types_for_property(listing_key="1611952")

        mock_get_unit_types.assert_called_once_with(
            filter_query="ListingKey eq '1611952'"
        )

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_unit_types_by_type(self, mock_get_unit_types: Mock) -> None:
        """Test get_unit_types_by_type functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        result = self.client.get_unit_types_by_type(
            unit_type="Condo", expand="Properties"
        )

        mock_get_unit_types.assert_called_once_with(
            filter_query="UnitType eq 'Condo'", expand="Properties"
        )

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_residential_unit_types(self, mock_get_unit_types: Mock) -> None:
        """Test get_residential_unit_types functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        result = self.client.get_residential_unit_types()

        # Check that the method was called with a complex filter
        mock_get_unit_types.assert_called_once()
        call_args = mock_get_unit_types.call_args
        assert "filter_query" in call_args.kwargs
        assert "UnitType eq 'Condo'" in call_args.kwargs["filter_query"]
        assert "UnitType eq 'Townhome'" in call_args.kwargs["filter_query"]

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_unit_types_with_properties(self, mock_get_unit_types: Mock) -> None:
        """Test get_unit_types_with_properties functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        result = self.client.get_unit_types_with_properties(top=10)

        mock_get_unit_types.assert_called_once_with(expand="Properties", top=10)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_modified_unit_types_datetime(self, mock_get_unit_types: Mock) -> None:
        """Test get_modified_unit_types with datetime object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        since_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = self.client.get_modified_unit_types(
            since=since_datetime, orderby="ModificationTimestamp desc"
        )

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_unit_types.assert_called_once_with(
            filter_query=expected_filter, orderby="ModificationTimestamp desc"
        )

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_modified_unit_types_date(self, mock_get_unit_types: Mock) -> None:
        """Test get_modified_unit_types with date object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        since_date = date(2024, 1, 1)
        result = self.client.get_modified_unit_types(since=since_date)

        expected_filter = "ModificationTimestamp gt '2024-01-01T00:00:00Z'"
        mock_get_unit_types.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.property_unit_types.PropertyUnitTypesClient.get_property_unit_types")
    def test_get_modified_unit_types_string(self, mock_get_unit_types: Mock) -> None:
        """Test get_modified_unit_types with string."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_unit_types.return_value = mock_response

        since_string = "2024-01-01T12:00:00Z"
        result = self.client.get_modified_unit_types(since=since_string)

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_unit_types.assert_called_once_with(filter_query=expected_filter)

    def test_init_default_params(self) -> None:
        """Test PropertyUnitTypesClient initialization with default parameters."""
        client = PropertyUnitTypesClient()
        # Test that it doesn't raise an exception and creates properly
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")

    def test_init_with_params(self) -> None:
        """Test PropertyUnitTypesClient initialization with custom parameters."""
        client = PropertyUnitTypesClient(
            bearer_token="custom_token", base_url="https://custom.api.com"
        )
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")
