"""Tests for deleted records client."""

import pytest
import responses
from datetime import datetime, timedelta

from wfrmls.deleted import DeletedClient, ResourceName
from wfrmls.exceptions import NotFoundError, ValidationError


class TestDeletedClientInit:
    """Test DeletedClient initialization."""

    def test_init_with_bearer_token(self) -> None:
        """Test initialization with provided bearer token."""
        client = DeletedClient(bearer_token="test_token")
        assert client.bearer_token == "test_token"

    def test_init_with_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = DeletedClient(
            bearer_token="test_token", 
            base_url="https://custom.api.com"
        )
        assert client.base_url == "https://custom.api.com"


class TestDeletedClient:
    """Test DeletedClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = DeletedClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_deleted_success(self) -> None:
        """Test successful get deleted records request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Deleted",
            "value": [
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": "12345678",
                    "DeletedDateTime": "2024-01-15T10:30:00Z"
                },
                {
                    "ResourceName": "Member",
                    "ResourceRecordKey": "87654321",
                    "DeletedDateTime": "2024-01-15T11:00:00Z"
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_deleted_with_odata_params(self) -> None:
        """Test get deleted records with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(
            top=10,
            skip=20,
            filter_query="ResourceName eq 'Property'",
            select=["ResourceName", "ResourceRecordKey", "DeletedDateTime"],
            orderby="DeletedDateTime desc",
            count=True
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=ResourceName+eq+%27Property%27" in request.url
        assert "ResourceName" in request.url
        assert "ResourceRecordKey" in request.url
        assert "DeletedDateTime" in request.url
        assert "%24orderby=DeletedDateTime+desc" in request.url
        assert "%24count=true" in request.url

    @responses.activate
    def test_get_deleted_by_resource_with_enum(self) -> None:
        """Test get deleted records by resource using enum."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name=ResourceName.PROPERTY,
            top=50
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=50" in request.url
        assert "%24filter=ResourceName+eq+%27Property%27" in request.url

    @responses.activate
    def test_get_deleted_by_resource_with_string(self) -> None:
        """Test get deleted records by resource using string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name="Member",
            orderby="DeletedDateTime desc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "ResourceName+eq+%27Member%27" in request.url or "ResourceName eq 'Member'" in request.url
        assert "DeletedDateTime+desc" in request.url or "DeletedDateTime desc" in request.url

    @responses.activate
    def test_get_deleted_since_with_datetime_string(self) -> None:
        """Test get deleted records since a datetime string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deleted_since(since=cutoff_time, top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert "$top=25" in request.url
        assert "DeletedDateTime+gt" in request.url

    @responses.activate
    def test_get_deleted_since_with_resource_filter(self) -> None:
        """Test get deleted records since a time with resource filter."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deleted_since(
            since=cutoff_time,
            resource_name=ResourceName.PROPERTY
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "DeletedDateTime+gt" in request.url
        assert "ResourceName+eq+%27Property%27" in request.url or "ResourceName eq 'Property'" in request.url

    @responses.activate
    def test_get_deleted_property_records(self) -> None:
        """Test get deleted property records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_property_records(top=30)

        assert result == mock_response
        request = responses.calls[0].request
        assert "$top=30" in request.url
        assert "ResourceName+eq+%27Property%27" in request.url or "ResourceName eq 'Property'" in request.url

    @responses.activate
    def test_get_deleted_member_records(self) -> None:
        """Test get deleted member records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_member_records(orderby="DeletedDateTime desc")

        assert result == mock_response
        request = responses.calls[0].request
        assert "ResourceName+eq+%27Member%27" in request.url or "ResourceName eq 'Member'" in request.url
        assert "DeletedDateTime+desc" in request.url or "DeletedDateTime desc" in request.url

    @responses.activate
    def test_get_deleted_office_records(self) -> None:
        """Test get deleted office records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_office_records(top=10)

        assert result == mock_response
        request = responses.calls[0].request
        assert "$top=10" in request.url
        assert "ResourceName+eq+%27Office%27" in request.url or "ResourceName eq 'Office'" in request.url

    @responses.activate
    def test_get_deleted_media_records(self) -> None:
        """Test get deleted media records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_media_records(top=100)

        assert result == mock_response
        request = responses.calls[0].request
        assert "$top=100" in request.url
        assert "ResourceName+eq+%27Media%27" in request.url or "ResourceName eq 'Media'" in request.url

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_deleted(top=500)

        assert result == mock_response
        request = responses.calls[0].request
        # Should be capped at 200
        assert "$top=200" in request.url

    @responses.activate
    def test_select_list_parameter(self) -> None:
        """Test select parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(
            select=["ResourceName", "ResourceRecordKey", "DeletedDateTime"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "ResourceName" in request.url
        assert "ResourceRecordKey" in request.url
        assert "DeletedDateTime" in request.url

    @responses.activate
    def test_deleted_not_found(self) -> None:
        """Test deleted records not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json={"error": {"message": "Resource not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_deleted(filter_query="ResourceName eq 'NonExistent'")

    def test_resource_name_enum_values(self) -> None:
        """Test ResourceName enum values are correct."""
        assert ResourceName.PROPERTY.value == "Property"
        assert ResourceName.MEMBER.value == "Member"
        assert ResourceName.OFFICE.value == "Office"
        assert ResourceName.OPENHOUSE.value == "OpenHouse"
        assert ResourceName.MEDIA.value == "Media"
        assert ResourceName.HISTORY_TRANSACTIONAL.value == "HistoryTransactional"
        assert ResourceName.PROPERTY_GREEN_VERIFICATION.value == "PropertyGreenVerification"
        assert ResourceName.PROPERTY_UNIT_TYPES.value == "PropertyUnitTypes"
        assert ResourceName.ADU.value == "Adu"

    @responses.activate
    def test_combined_filters(self) -> None:
        """Test combining resource filter with additional filters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name=ResourceName.PROPERTY,
            filter_query="DeletedDateTime gt 2024-01-01T00:00:00Z"
        )

        assert result == mock_response
        request = responses.calls[0].request
        # Should contain both filters combined with 'and'
        assert "ResourceName" in request.url
        assert "Property" in request.url
        assert "DeletedDateTime" in request.url 