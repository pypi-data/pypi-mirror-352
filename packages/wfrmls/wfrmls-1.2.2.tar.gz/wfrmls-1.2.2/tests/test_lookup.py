"""Tests for lookup client."""

from datetime import date, datetime, timedelta

import pytest
import responses

from wfrmls.exceptions import NotFoundError, ValidationError, WFRMLSError
from wfrmls.lookup import LookupClient


class TestLookupClient:
    """Test cases for LookupClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = LookupClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_lookups_success(self) -> None:
        """Test successful get lookups request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Lookup",
            "value": [
                {"LookupKey": "12345", "LookupName": "PropertyType", "LookupValue": "Residential"},
                {"LookupKey": "23456", "LookupName": "PropertyType", "LookupValue": "Commercial"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_lookups_with_odata_params(self) -> None:
        """Test get lookups with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups(
            top=10,
            skip=20,
            filter_query="LookupName eq 'PropertyType'",
            select=["LookupKey", "LookupName", "LookupValue"],
            orderby="LookupValue desc",
            expand=["Resource", "Field"],
            count=True
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=LookupName+eq+%27PropertyType%27" in request.url
        assert "LookupKey" in request.url
        assert "LookupName" in request.url
        assert "LookupValue" in request.url
        assert "%24orderby=LookupValue+desc" in request.url
        assert "%24expand=Resource%2CField" in request.url
        assert "%24count=true" in request.url

    @responses.activate
    def test_get_lookups_with_expand_string(self) -> None:
        """Test get lookups with expand parameter as string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups(expand="Resource")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "Resource" in request.url

    @responses.activate
    def test_get_lookups_with_select_string(self) -> None:
        """Test get lookups with select parameter as string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups(select="LookupKey,LookupName")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "LookupKey" in request.url
        assert "LookupName" in request.url

    @responses.activate
    def test_get_lookups_count_false(self) -> None:
        """Test get lookups with count=False."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups(count=False)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24count=false" in request.url

    @responses.activate
    def test_get_lookup_success(self) -> None:
        """Test successful get single lookup by key."""
        mock_response = {
            "LookupKey": "PROP_TYPE_RESIDENTIAL",
            "LookupName": "PropertyType",
            "LookupValue": "Residential",
            "StandardLookupValue": "Residential"
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup('PROP_TYPE_RESIDENTIAL')",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookup("PROP_TYPE_RESIDENTIAL")
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_lookup_not_found(self) -> None:
        """Test get lookup not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup('nonexistent')",
            json={"error": {"message": "Lookup not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_lookup("nonexistent")

    @responses.activate
    def test_get_lookups_by_name_success(self) -> None:
        """Test get lookups by name."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups_by_name(
            lookup_name="PropertyType", 
            top=25,
            orderby="DisplayOrder asc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "LookupName+eq+%27PropertyType%27" in request.url or "LookupName eq 'PropertyType'" in request.url
        assert "%24top=25" in request.url

    @responses.activate
    def test_get_lookups_by_name_with_existing_filter(self) -> None:
        """Test get lookups by name with existing filter query."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups_by_name(
            lookup_name="PropertyType",
            filter_query="LookupValue eq 'Residential'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "LookupName" in request.url
        assert "PropertyType" in request.url
        assert "LookupValue" in request.url
        assert "Residential" in request.url

    @responses.activate
    def test_get_property_type_lookups(self) -> None:
        """Test get property type lookups convenience method."""
        mock_response = {
            "@odata.context": "test", 
            "value": [
                {"LookupKey": "PT_RES", "LookupValue": "Residential"},
                {"LookupKey": "PT_COM", "LookupValue": "Commercial"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_property_type_lookups(orderby="DisplayOrder asc")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "PropertyType" in request.url

    @responses.activate
    def test_get_property_status_lookups(self) -> None:
        """Test get property status lookups convenience method."""
        mock_response = {
            "@odata.context": "test", 
            "value": [
                {"LookupKey": "PS_ACT", "LookupValue": "Active"},
                {"LookupKey": "PS_PEN", "LookupValue": "Pending"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_property_status_lookups()

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "PropertyStatus" in request.url

    @responses.activate
    def test_get_standard_lookups_success(self) -> None:
        """Test get standard RESO lookup values."""
        mock_response = {
            "@odata.context": "test", 
            "value": [
                {"LookupKey": "STD_1", "StandardLookupValue": "Active"},
                {"LookupKey": "STD_2", "StandardLookupValue": "Pending"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_standard_lookups()

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should filter for records with StandardLookupValue not null
        assert "StandardLookupValue+ne+null" in request.url or "StandardLookupValue ne null" in request.url

    @responses.activate
    def test_get_standard_lookups_with_existing_filter(self) -> None:
        """Test get standard lookups with existing filter query."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_standard_lookups(
            filter_query="LookupName eq 'PropertyType'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "StandardLookupValue" in request.url
        assert "LookupName" in request.url
        assert "PropertyType" in request.url

    @responses.activate
    def test_get_active_lookups_success(self) -> None:
        """Test get active lookup values."""
        mock_response = {
            "@odata.context": "test", 
            "value": [
                {"LookupKey": "ACT_1", "IsActive": True},
                {"LookupKey": "ACT_2", "IsActive": True}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_active_lookups(
            orderby="LookupName asc, DisplayOrder asc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should filter for active records
        assert "IsActive+eq+true" in request.url or "IsActive eq true" in request.url

    @responses.activate
    def test_get_active_lookups_with_existing_filter(self) -> None:
        """Test get active lookups with existing filter query."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_active_lookups(
            filter_query="LookupName eq 'PropertyStatus'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "IsActive" in request.url
        assert "LookupName" in request.url
        assert "PropertyStatus" in request.url

    @responses.activate
    def test_get_lookup_names(self) -> None:
        """Test get unique lookup names."""
        mock_response = {
            "@odata.context": "test", 
            "value": [
                {"LookupName": "PropertyType"},
                {"LookupName": "PropertyStatus"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookup_names()

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24select=LookupName" in request.url
        assert "%24orderby=LookupName+asc" in request.url

    @responses.activate
    def test_get_modified_lookups_with_datetime(self) -> None:
        """Test get modified lookups with datetime object."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        since_datetime = datetime(2024, 1, 15, 10, 30, 0)
        result = self.client.get_modified_lookups(since=since_datetime)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt" in request.url
        assert "2024-01-15T10%3A30%3A00Z" in request.url

    @responses.activate
    def test_get_modified_lookups_with_date(self) -> None:
        """Test get modified lookups with date object."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        since_date = date(2024, 1, 15)
        result = self.client.get_modified_lookups(
            since=since_date,
            orderby="ModificationTimestamp desc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt" in request.url
        assert "2024-01-15T00%3A00%3A00Z" in request.url

    @responses.activate
    def test_get_modified_lookups_with_string(self) -> None:
        """Test get modified lookups with datetime string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        since_string = "2023-01-01T00:00:00Z"
        result = self.client.get_modified_lookups(since=since_string)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt" in request.url
        assert "2023-01-01T00%3A00%3A00Z" in request.url

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_lookups(top=500)

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
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups(
            select=["LookupKey", "LookupName", "LookupValue"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "LookupKey" in request.url
        assert "LookupName" in request.url
        assert "LookupValue" in request.url

    @responses.activate
    def test_expand_list_parameter(self) -> None:
        """Test expand parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json=mock_response,
            status=200,
        )

        result = self.client.get_lookups(expand=["Resource", "Field"])

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24expand=Resource%2CField" in request.url

    @responses.activate
    def test_lookup_client_error_handling(self) -> None:
        """Test lookup client error handling."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json={"error": {"message": "Server error"}},
            status=500,
        )

        with pytest.raises(Exception):  # Will be ServerError
            self.client.get_lookups()

    @responses.activate
    def test_lookup_validation_error(self) -> None:
        """Test lookup validation error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Lookup",
            json={"error": {"message": "Invalid query parameter"}},
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request"):
            self.client.get_lookups(filter_query="invalid syntax") 