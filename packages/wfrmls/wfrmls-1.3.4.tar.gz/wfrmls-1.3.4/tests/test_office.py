"""Tests for office client."""

from datetime import date

import pytest
import responses

from wfrmls.exceptions import NotFoundError, ValidationError
from wfrmls.office import OfficeClient, OfficeStatus, OfficeType


class TestOfficeClient:
    """Test cases for OfficeClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = OfficeClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_offices_success(self) -> None:
        """Test successful get offices request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Office",
            "value": [
                {
                    "OfficeKey": "12345",
                    "OfficeName": "ABC Realty",
                    "OfficeStatus": "Active",
                },
                {
                    "OfficeKey": "67890",
                    "OfficeName": "XYZ Properties",
                    "OfficeStatus": "Active",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.get_offices()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_offices_with_odata_params(self) -> None:
        """Test get offices with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.get_offices(
            top=10,
            skip=20,
            filter_query="OfficeStatus eq 'Active'",
            select=["OfficeKey", "OfficeName", "OfficePhone"],
            orderby="OfficeName desc",
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=OfficeStatus+eq+%27Active%27" in request.url
        assert "OfficeKey" in request.url
        assert "OfficeName" in request.url
        assert "OfficePhone" in request.url
        assert "%24orderby=OfficeName+desc" in request.url

    @responses.activate
    def test_get_office_not_found(self) -> None:
        """Test get office not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office('nonexistent')",
            json={"error": {"message": "Office not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_office("nonexistent")

    @responses.activate
    def test_get_active_offices(self) -> None:
        """Test get active offices convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.get_active_offices(top=50)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert (
            "%24filter=OfficeStatus+eq+%27Active%27" in request.url
            or "OfficeStatus+eq+%27Active%27" in request.url
        )
        assert "%24top=50" in request.url

    @responses.activate
    def test_search_offices_by_name(self) -> None:
        """Test search offices by name."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.search_offices_by_name(name="ABC Realty")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "contains" in request.url
        assert "OfficeName" in request.url
        assert "ABC+Realty" in request.url or "ABC Realty" in request.url

    @responses.activate
    def test_get_offices_with_members(self) -> None:
        """Test get offices with member info expanded."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.get_offices_with_members(top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24expand=Members" in request.url or "$expand=Members" in request.url
        assert "%24top=25" in request.url

    @responses.activate
    def test_get_modified_offices(self) -> None:
        """Test get modified offices."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        test_date = date(2023, 1, 1)
        result = self.client.get_modified_offices(since=test_date)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt+2023-01-01Z" in request.url

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        assert OfficeStatus.ACTIVE.value == "Active"
        assert OfficeStatus.INACTIVE.value == "Inactive"

        assert OfficeType.MAIN.value == "Main"
        assert OfficeType.BRANCH.value == "Branch"
        assert OfficeType.FRANCHISE.value == "Franchise"

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_offices(top=500)

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
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.get_offices(
            select=["OfficeKey", "OfficeName", "OfficePhone"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "OfficeKey" in request.url
        assert "OfficeName" in request.url
        assert "OfficePhone" in request.url

    @responses.activate
    def test_expand_list_parameter(self) -> None:
        """Test expand parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.get_offices(expand=["Members", "Properties"])

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24expand=Members%2CProperties" in request.url

    @responses.activate
    def test_combined_filters_in_name_search(self) -> None:
        """Test combining name filter with additional filters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Office",
            json=mock_response,
            status=200,
        )

        result = self.client.search_offices_by_name(
            name="ABC", filter_query="OfficeStatus eq 'Active'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "OfficeName" in request.url
        assert "ABC" in request.url
        assert "OfficeStatus" in request.url
        assert "Active" in request.url
