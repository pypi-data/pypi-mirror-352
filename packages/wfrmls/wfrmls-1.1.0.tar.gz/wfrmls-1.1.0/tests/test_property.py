"""Tests for property client."""

import pytest
import responses
from datetime import date

from wfrmls.properties import PropertyClient, PropertyStatus, PropertyType
from wfrmls.exceptions import NotFoundError, ValidationError


class TestPropertyClient:
    """Test cases for PropertyClient."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = PropertyClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_properties_success(self) -> None:
        """Test successful get properties request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Property",
            "value": [
                {"ListingId": "12345678", "ListPrice": 250000, "StandardStatus": "Active"},
                {"ListingId": "87654321", "ListPrice": 300000, "StandardStatus": "Pending"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_properties_with_odata_params(self) -> None:
        """Test get properties with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties(
            top=10,
            skip=20,
            filter_query="StandardStatus eq 'Active'",
            select=["ListingId", "ListPrice"],
            orderby="ListPrice desc"
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=StandardStatus+eq+%27Active%27" in request.url
        assert "%24select=ListingId%2CListPrice" in request.url
        assert "%24orderby=ListPrice+desc" in request.url

    @responses.activate
    def test_get_property_not_found(self) -> None:
        """Test get property not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property('nonexistent')",
            json={"error": {"message": "Property not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_property("nonexistent")

    @responses.activate
    def test_search_properties_by_radius(self) -> None:
        """Test geolocation radius search."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.search_properties_by_radius(
            latitude=40.7608,
            longitude=-111.8910,
            radius_miles=10,
            additional_filters="StandardStatus eq 'Active'"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "geo.distance" in request.url
        assert "40.7608" in request.url
        assert "-111.891" in request.url  # URL encoding may truncate trailing zero
        assert "le+10" in request.url
        assert "StandardStatus+eq+%27Active%27" in request.url

    @responses.activate
    def test_search_properties_by_polygon(self) -> None:
        """Test geolocation polygon search."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        polygon = [
            {"lat": 40.7608, "lng": -111.8910},
            {"lat": 40.7708, "lng": -111.8810},
            {"lat": 40.7508, "lng": -111.8710},
            {"lat": 40.7608, "lng": -111.8910}
        ]

        result = self.client.search_properties_by_polygon(polygon_coordinates=polygon)

        assert result == mock_response
        request = responses.calls[0].request
        assert "geo.intersects" in request.url
        assert "POLYGON" in request.url

    @responses.activate
    def test_get_active_properties(self) -> None:
        """Test get active properties convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_active_properties(top=50)

        assert result == mock_response
        request = responses.calls[0].request
        assert "%24filter=StandardStatus+eq+%27Active%27" in request.url or "StandardStatus+eq+%27Active%27" in request.url
        assert "$top=50" in request.url

    @responses.activate
    def test_get_properties_by_price_range(self) -> None:
        """Test price range filtering."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_price_range(
            min_price=200000,
            max_price=500000
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "ListPrice+ge+200000" in request.url
        assert "ListPrice+le+500000" in request.url

    @responses.activate
    def test_get_properties_by_city(self) -> None:
        """Test city filtering."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_city("Salt Lake City")

        assert result == mock_response
        request = responses.calls[0].request
        assert "City+eq+%27Salt+Lake+City%27" in request.url

    @responses.activate
    def test_get_modified_properties(self) -> None:
        """Test modified properties filtering."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        test_date = date(2023, 1, 1)
        result = self.client.get_modified_properties(since=test_date)

        assert result == mock_response
        request = responses.calls[0].request
        assert "ModificationTimestamp+gt+2023-01-01Z" in request.url

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        assert PropertyStatus.ACTIVE.value == "Active"
        assert PropertyStatus.PENDING.value == "Pending"
        assert PropertyType.RESIDENTIAL.value == "Residential"
        assert PropertyType.COMMERCIAL.value == "Commercial"

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_properties(top=500)

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
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties(
            select=["ListingId", "ListPrice", "StandardStatus"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "$select=ListingId%2CListPrice%2CStandardStatus" in request.url

    @responses.activate
    def test_expand_list_parameter(self) -> None:
        """Test expand parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties(expand=["Media", "Member"])

        assert result == mock_response
        request = responses.calls[0].request
        assert "$expand=Media%2CMember" in request.url 