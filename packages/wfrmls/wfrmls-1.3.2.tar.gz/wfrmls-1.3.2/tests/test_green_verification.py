"""Tests for WFRMLS Green Verification module."""

from datetime import date, datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from wfrmls.exceptions import WFRMLSError
from wfrmls.green_verification import GreenVerificationClient, GreenVerificationType


class TestGreenVerificationType:
    """Test suite for GreenVerificationType enum."""

    def test_green_verification_type_values(self) -> None:
        """Test GreenVerificationType enum values."""
        assert GreenVerificationType.ENERGY_STAR.value == "Energy Star"
        assert GreenVerificationType.LEED.value == "LEED"
        assert GreenVerificationType.GREEN_BUILDING.value == "Green Building"
        assert GreenVerificationType.HERS.value == "HERS"
        assert GreenVerificationType.OTHER.value == "Other"


class TestGreenVerificationClient:
    """Test suite for GreenVerificationClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = GreenVerificationClient(bearer_token="test_token")

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verifications_basic(self, mock_get: Mock) -> None:
        """Test basic get_green_verifications functionality."""
        mock_response: Dict[str, Any] = {
            "value": [
                {
                    "GreenVerificationKey": "GV123",
                    "GreenVerificationType": "ENERGY_STAR",
                    "GreenVerificationStatus": "Active",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_green_verifications()

        mock_get.assert_called_once_with("PropertyGreenVerification", params={})
        assert result == mock_response

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verifications_with_all_params(self, mock_get: Mock) -> None:
        """Test get_green_verifications with all parameters."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get.return_value = mock_response

        result = self.client.get_green_verifications(
            top=50,
            skip=10,
            filter_query="GreenVerificationStatus eq 'Active'",
            select=["GreenVerificationKey", "GreenVerificationType"],
            orderby="GreenVerificationType asc",
            expand=["Property"],
            count=True,
        )

        expected_params = {
            "$top": 50,
            "$skip": 10,
            "$filter": "GreenVerificationStatus eq 'Active'",
            "$select": "GreenVerificationKey,GreenVerificationType",
            "$orderby": "GreenVerificationType asc",
            "$expand": "Property",
            "$count": "true",
        }

        mock_get.assert_called_once_with(
            "PropertyGreenVerification", params=expected_params
        )

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verifications_top_limit_enforcement(
        self, mock_get: Mock
    ) -> None:
        """Test that top parameter is limited to 200."""
        mock_get.return_value = {"value": []}

        self.client.get_green_verifications(top=300)

        expected_params = {"$top": 200}
        mock_get.assert_called_once_with(
            "PropertyGreenVerification", params=expected_params
        )

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verifications_select_string(self, mock_get: Mock) -> None:
        """Test get_green_verifications with select as string."""
        mock_get.return_value = {"value": []}

        self.client.get_green_verifications(
            select="GreenVerificationKey,GreenVerificationType"
        )

        expected_params = {"$select": "GreenVerificationKey,GreenVerificationType"}
        mock_get.assert_called_once_with(
            "PropertyGreenVerification", params=expected_params
        )

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verifications_expand_string(self, mock_get: Mock) -> None:
        """Test get_green_verifications with expand as string."""
        mock_get.return_value = {"value": []}

        self.client.get_green_verifications(expand="Property,Member")

        expected_params = {"$expand": "Property,Member"}
        mock_get.assert_called_once_with(
            "PropertyGreenVerification", params=expected_params
        )

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verifications_count_false(self, mock_get: Mock) -> None:
        """Test get_green_verifications with count=False."""
        mock_get.return_value = {"value": []}

        self.client.get_green_verifications(count=False)

        expected_params = {"$count": "false"}
        mock_get.assert_called_once_with(
            "PropertyGreenVerification", params=expected_params
        )

    @patch("wfrmls.green_verification.GreenVerificationClient.get")
    def test_get_green_verification(self, mock_get: Mock) -> None:
        """Test get_green_verification functionality."""
        verification_key = "GV123"
        mock_response: Dict[str, Any] = {
            "GreenVerificationKey": verification_key,
            "GreenVerificationType": "ENERGY_STAR",
            "GreenVerificationStatus": "Active",
        }
        mock_get.return_value = mock_response

        result = self.client.get_green_verification(verification_key)

        mock_get.assert_called_once_with(
            f"PropertyGreenVerification('{verification_key}')"
        )
        assert result == mock_response

    @patch("wfrmls.green_verification.GreenVerificationClient.get_green_verifications")
    def test_get_verifications_for_property(self, mock_get_verifications: Mock) -> None:
        """Test get_verifications_for_property functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_verifications.return_value = mock_response

        result = self.client.get_verifications_for_property(
            listing_key="12345", orderby="GreenVerificationType asc"
        )

        mock_get_verifications.assert_called_once_with(
            filter_query="ListingKey eq '12345'", orderby="GreenVerificationType asc"
        )

    @patch("wfrmls.green_verification.GreenVerificationClient.get_green_verifications")
    def test_get_verifications_for_property_with_existing_filter(
        self, mock_get_verifications: Mock
    ) -> None:
        """Test get_verifications_for_property with existing filter_query."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_verifications.return_value = mock_response

        result = self.client.get_verifications_for_property(
            listing_key="12345", filter_query="GreenVerificationStatus eq 'Active'"
        )

        expected_filter = (
            "ListingKey eq '12345' and GreenVerificationStatus eq 'Active'"
        )
        mock_get_verifications.assert_called_once_with(filter_query=expected_filter)

    def test_init_default_params(self) -> None:
        """Test GreenVerificationClient initialization with default parameters."""
        client = GreenVerificationClient()
        # Test that it doesn't raise an exception and creates properly
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")

    def test_init_with_params(self) -> None:
        """Test GreenVerificationClient initialization with custom parameters."""
        client = GreenVerificationClient(
            bearer_token="custom_token", base_url="https://custom.api.com"
        )
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")
