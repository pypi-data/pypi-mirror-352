"""Tests for openhouse client."""

from datetime import date, datetime

import pytest
import responses

from wfrmls.exceptions import NotFoundError, ValidationError
from wfrmls.openhouse import (
    OpenHouseAttendedBy,
    OpenHouseClient,
    OpenHouseStatus,
    OpenHouseType,
)


class TestOpenHouseClient:
    """Test cases for OpenHouseClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = OpenHouseClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_open_houses_success(self) -> None:
        """Test successful get open houses request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#OpenHouse",
            "value": [
                {
                    "OpenHouseKey": "12345",
                    "ListingKey": "67890",
                    "OpenHouseDate": "2024-01-15",
                    "OpenHouseStatus": "Active",
                },
                {
                    "OpenHouseKey": "23456",
                    "ListingKey": "78901",
                    "OpenHouseDate": "2024-01-16",
                    "OpenHouseStatus": "Active",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_open_houses_with_odata_params(self) -> None:
        """Test get open houses with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses(
            top=10,
            skip=20,
            filter_query="OpenHouseStatus eq 'Active'",
            select=["OpenHouseKey", "ListingKey", "OpenHouseDate"],
            orderby="OpenHouseDate desc",
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=OpenHouseStatus+eq+%27Active%27" in request.url
        assert "OpenHouseKey" in request.url
        assert "ListingKey" in request.url
        assert "OpenHouseDate" in request.url
        assert "%24orderby=OpenHouseDate+desc" in request.url

    @responses.activate
    def test_get_open_house_not_found(self) -> None:
        """Test get open house not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse('nonexistent')",
            json={"error": {"message": "OpenHouse not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_open_house("nonexistent")

    @responses.activate
    def test_get_upcoming_open_houses(self) -> None:
        """Test get upcoming open houses convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_upcoming_open_houses(days_ahead=7, top=50)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "OpenHouseDate+ge" in request.url
        assert "%24top=50" in request.url

    @responses.activate
    def test_get_open_houses_for_property(self) -> None:
        """Test get open houses for a specific property."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses_for_property(listing_key="12345", top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListingKey+eq+%27" in request.url or "ListingKey eq '" in request.url
        assert "12345" in request.url
        assert "%24top=25" in request.url

    @responses.activate
    def test_get_open_houses_by_agent(self) -> None:
        """Test get open houses by agent."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses_by_agent(agent_key="67890")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert (
            "ShowingAgentKey+eq+%27" in request.url
            or "ShowingAgentKey eq '" in request.url
        )
        assert "67890" in request.url

    @responses.activate
    def test_get_open_houses_by_date_range(self) -> None:
        """Test get open houses by date range."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        result = self.client.get_open_houses_by_date_range(
            start_date=start_date, end_date=end_date
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "OpenHouseDate+ge+2024-01-01" in request.url
        assert "OpenHouseDate+le+2024-01-31" in request.url

    @responses.activate
    def test_get_weekend_open_houses(self) -> None:
        """Test get weekend open houses convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_weekend_open_houses(weeks_ahead=2)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "OpenHouseDate+ge" in request.url

    @responses.activate
    def test_get_modified_open_houses(self) -> None:
        """Test get modified open houses."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        test_date = date(2023, 1, 1)
        result = self.client.get_modified_open_houses(since=test_date)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt+%272023-01-01T00%3A00%3A00Z%27" in request.url

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        assert OpenHouseStatus.ACTIVE.value == "Active"
        assert OpenHouseStatus.CANCELLED.value == "Cancelled"
        assert OpenHouseStatus.COMPLETED.value == "Completed"

        assert OpenHouseType.PUBLIC.value == "Public"
        assert OpenHouseType.PRIVATE.value == "Private"
        assert OpenHouseType.BROKER.value == "Broker"

        assert OpenHouseAttendedBy.LISTING_AGENT.value == "ListingAgent"
        assert OpenHouseAttendedBy.BUYER_AGENT.value == "BuyerAgent"

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_open_houses(top=500)

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
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses(
            select=["OpenHouseKey", "ListingKey", "OpenHouseDate"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "OpenHouseKey" in request.url
        assert "ListingKey" in request.url
        assert "OpenHouseDate" in request.url

    @responses.activate
    def test_expand_list_parameter(self) -> None:
        """Test expand parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses(expand=["Property", "Member"])

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
            "https://resoapi.utahrealestate.com/reso/odata/OpenHouse",
            json=mock_response,
            status=200,
        )

        result = self.client.get_open_houses_for_property(
            listing_key="12345", filter_query="OpenHouseStatus eq 'Active'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "ListingKey" in request.url
        assert "12345" in request.url
        assert "OpenHouseStatus" in request.url
        assert "Active" in request.url
