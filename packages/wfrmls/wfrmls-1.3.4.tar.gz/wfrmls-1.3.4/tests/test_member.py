"""Tests for member client."""

from datetime import date

import pytest
import responses

from wfrmls.exceptions import NotFoundError, ValidationError
from wfrmls.member import MemberClient, MemberStatus, MemberType


class TestMemberClient:
    """Test cases for MemberClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = MemberClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_members_success(self) -> None:
        """Test successful get members request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Member",
            "value": [
                {
                    "MemberKey": "12345",
                    "MemberFirstName": "John",
                    "MemberLastName": "Doe",
                    "MemberStatus": "Active",
                },
                {
                    "MemberKey": "67890",
                    "MemberFirstName": "Jane",
                    "MemberLastName": "Smith",
                    "MemberStatus": "Active",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_members_with_odata_params(self) -> None:
        """Test get members with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members(
            top=10,
            skip=20,
            filter_query="MemberStatus eq 'Active'",
            select=["MemberKey", "MemberFirstName", "MemberLastName"],
            orderby="MemberLastName desc",
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=MemberStatus+eq+%27Active%27" in request.url
        assert "MemberKey" in request.url
        assert "MemberFirstName" in request.url
        assert "MemberLastName" in request.url
        assert "%24orderby=MemberLastName+desc" in request.url

    @responses.activate
    def test_get_member_not_found(self) -> None:
        """Test get member not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member('nonexistent')",
            json={"error": {"message": "Member not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_member("nonexistent")

    @responses.activate
    def test_get_active_members(self) -> None:
        """Test get active members convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_active_members(top=50)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert (
            "%24filter=MemberStatus+eq+%27Active%27" in request.url
            or "MemberStatus+eq+%27Active%27" in request.url
        )
        assert "%24top=50" in request.url

    @responses.activate
    def test_get_members_by_office(self) -> None:
        """Test get members by office."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members_by_office(office_key="12345", top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "OfficeKey+eq+%27" in request.url or "OfficeKey eq '" in request.url
        assert "12345" in request.url
        assert "%24top=25" in request.url

    @responses.activate
    def test_search_members_by_name(self) -> None:
        """Test search members by name."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.search_members_by_name(
            first_name="John", last_name="Smith"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "contains" in request.url
        assert "MemberFirstName" in request.url
        assert "MemberLastName" in request.url
        assert "John" in request.url
        assert "Smith" in request.url

    @responses.activate
    def test_search_members_by_last_name_only(self) -> None:
        """Test search members by last name only."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.search_members_by_name(last_name="Smith")

        assert result == mock_response
        request = responses.calls[0].request
        assert "contains" in request.url
        assert "MemberLastName" in request.url
        assert "Smith" in request.url

    @responses.activate
    def test_get_members_with_office(self) -> None:
        """Test get members with office info expanded."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members_with_office(top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert "%24expand=Office" in request.url or "$expand=Office" in request.url
        assert "%24top=25" in request.url

    @responses.activate
    def test_get_modified_members(self) -> None:
        """Test get modified members."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        test_date = date(2023, 1, 1)
        result = self.client.get_modified_members(since=test_date)

        assert result == mock_response
        request = responses.calls[0].request
        assert "ModificationTimestamp+gt+2023-01-01Z" in request.url

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        assert MemberStatus.ACTIVE.value == "Active"
        assert MemberStatus.INACTIVE.value == "Inactive"
        assert MemberStatus.SUSPENDED.value == "Suspended"

        assert MemberType.AGENT.value == "Agent"
        assert MemberType.BROKER.value == "Broker"
        assert MemberType.ASSISTANT.value == "Assistant"

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_members(top=500)

        assert result == mock_response
        request = responses.calls[0].request
        # Should be capped at 200
        assert "%24top=200" in request.url or "$top=200" in request.url

    @responses.activate
    def test_select_list_parameter(self) -> None:
        """Test select parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members(
            select=["MemberKey", "MemberFirstName", "MemberLastName"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "MemberKey" in request.url
        assert "MemberFirstName" in request.url
        assert "MemberLastName" in request.url

    @responses.activate
    def test_expand_list_parameter(self) -> None:
        """Test expand parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members(expand=["Office", "Property"])

        assert result == mock_response
        request = responses.calls[0].request
        assert "%24expand=Office%2CProperty" in request.url

    @responses.activate
    def test_combined_filters_in_office_search(self) -> None:
        """Test combining office filter with additional filters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Member",
            json=mock_response,
            status=200,
        )

        result = self.client.get_members_by_office(
            office_key="12345", filter_query="MemberStatus eq 'Active'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        # Should contain both filters combined with 'and'
        assert "OfficeKey" in request.url
        assert "12345" in request.url
        assert "MemberStatus" in request.url
        assert "Active" in request.url
