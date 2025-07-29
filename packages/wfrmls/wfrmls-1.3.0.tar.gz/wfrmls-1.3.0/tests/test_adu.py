"""Tests for ADU client."""

from datetime import date

import pytest
import responses

from wfrmls.exceptions import NotFoundError, ValidationError
from wfrmls.adu import AduClient, AduStatus, AduType


class TestAduClient:
    """Test cases for AduClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = AduClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_adus_success(self) -> None:
        """Test successful get ADUs request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Adu",
            "value": [
                {"AduKey": "12345", "ListingKey": "67890", "AduType": "Apartment", "AduStatus": "Active"},
                {"AduKey": "23456", "ListingKey": "78901", "AduType": "Cottage", "AduStatus": "Active"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_adus_with_odata_params(self) -> None:
        """Test get ADUs with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus(
            top=10,
            skip=20,
            filter_query="AduStatus eq 'Active'",
            select=["AduKey", "ListingKey", "AduType"],
            orderby="AduType desc"
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=AduStatus+eq+%27Active%27" in request.url
        assert "AduKey" in request.url
        assert "ListingKey" in request.url
        assert "AduType" in request.url
        assert "%24orderby=AduType+desc" in request.url

    @responses.activate
    def test_get_adu_not_found(self) -> None:
        """Test get ADU not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu('nonexistent')",
            json={"error": {"message": "ADU not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_adu("nonexistent")

    @responses.activate
    def test_get_existing_adus(self) -> None:
        """Test get existing ADUs convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_existing_adus(top=50)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24filter=AduStatus+eq+%27Existing%27" in request.url or "AduStatus+eq+%27Existing%27" in request.url
        assert "%24top=50" in request.url

    @responses.activate
    def test_get_adus_for_property(self) -> None:
        """Test get ADUs for a specific property."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus_for_property(listing_key="12345", top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListingKey+eq+%27" in request.url or "ListingKey eq '" in request.url
        assert "12345" in request.url
        assert "%24top=25" in request.url

    @responses.activate
    def test_get_adus_by_type(self) -> None:
        """Test get ADUs by type."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus_by_type(adu_type="Detached")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "AduType+eq+%27" in request.url or "AduType eq '" in request.url
        assert "Detached" in request.url

    @responses.activate
    def test_get_modified_adus(self) -> None:
        """Test get modified ADUs."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        test_date = date(2023, 1, 1)
        result = self.client.get_modified_adus(since=test_date)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt+%272023-01-01T00%3A00%3A00Z%27" in request.url

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        assert AduStatus.EXISTING.value == "Existing"
        assert AduStatus.PERMITTED.value == "Permitted"
        assert AduStatus.PLANNED.value == "Planned"
        assert AduStatus.UNDER_CONSTRUCTION.value == "Under Construction"
        
        assert AduType.DETACHED.value == "Detached"
        assert AduType.ATTACHED.value == "Attached"
        assert AduType.GARAGE_CONVERSION.value == "Garage Conversion"
        assert AduType.BASEMENT.value == "Basement"
        assert AduType.INTERIOR.value == "Interior"

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_adus(top=500)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should be capped at 200
        assert "%24top=200" in request.url or "$top=200" in request.url

    @responses.activate
    def test_select_list_parameter(self) -> None:
        """Test select parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus(
            select=["AduKey", "ListingKey", "AduType"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "AduKey" in request.url
        assert "ListingKey" in request.url
        assert "AduType" in request.url

    @responses.activate
    def test_expand_list_parameter(self) -> None:
        """Test expand parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus(expand=["Property", "Member"])

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24expand=Property%2CMember" in request.url

    @responses.activate
    def test_combined_filters_in_property_search(self) -> None:
        """Test combining property filter with additional filters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Adu",
            json=mock_response,
            status=200,
        )

        result = self.client.get_adus_for_property(
            listing_key="12345",
            filter_query="AduStatus eq 'Existing'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "ListingKey" in request.url
        assert "12345" in request.url
        assert "AduStatus" in request.url
        assert "Existing" in request.url 