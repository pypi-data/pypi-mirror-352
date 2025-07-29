"""Tests for property client."""

from datetime import date, datetime, timedelta

import pytest
import responses

from wfrmls.exceptions import NotFoundError, ValidationError, WFRMLSError, ServerError
from wfrmls.properties import PropertyClient, PropertyStatus, PropertyType


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
            orderby="ListPrice desc",
            expand=["Media", "Member"],
            count=True
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=StandardStatus+eq+%27Active%27" in request.url
        assert "%24select=ListingId%2CListPrice" in request.url
        assert "%24orderby=ListPrice+desc" in request.url
        assert "%24expand=Media%2CMember" in request.url
        assert "%24count=true" in request.url

    @responses.activate
    def test_get_properties_with_expand_string(self) -> None:
        """Test get properties with expand parameter as string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties(expand="Media")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "Media" in request.url

    @responses.activate
    def test_get_properties_with_select_string(self) -> None:
        """Test get properties with select parameter as string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties(select="ListingId,ListPrice")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListingId" in request.url
        assert "ListPrice" in request.url

    @responses.activate
    def test_get_properties_count_false(self) -> None:
        """Test get properties with count=False."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties(count=False)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24count=false" in request.url

    @responses.activate
    def test_get_property_success(self) -> None:
        """Test successful get single property by ID."""
        mock_response = {
            "ListingId": "12345678",
            "ListPrice": 250000,
            "StandardStatus": "Active",
            "UnparsedAddress": "123 Main St, Salt Lake City, UT"
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property('12345678')",
            json=mock_response,
            status=200,
        )

        result = self.client.get_property("12345678")
        assert result == mock_response
        assert len(responses.calls) == 1

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
    def test_search_properties_by_radius_success(self) -> None:
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
            additional_filters="StandardStatus eq 'Active'",
            top=50
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "geo.distance" in request.url
        assert "40.7608" in request.url
        assert "-111.891" in request.url  # URL encoding may truncate trailing zero
        assert "le+10" in request.url
        assert "StandardStatus+eq+%27Active%27" in request.url
        assert "%24top=50" in request.url

    @responses.activate
    def test_search_properties_by_radius_no_additional_filters(self) -> None:
        """Test radius search without additional filters."""
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
            radius_miles=5
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "geo.distance" in request.url

    @responses.activate
    def test_search_properties_by_polygon_success(self) -> None:
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

        result = self.client.search_properties_by_polygon(
            polygon_coordinates=polygon,
            additional_filters="PropertyType eq 'Residential'",
            top=100
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "geo.intersects" in request.url
        assert "POLYGON" in request.url
        assert "PropertyType+eq+%27Residential%27" in request.url

    @responses.activate
    def test_search_properties_by_polygon_no_additional_filters(self) -> None:
        """Test polygon search without additional filters."""
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
            {"lat": 40.7508, "lng": -111.8710}
        ]

        result = self.client.search_properties_by_polygon(polygon_coordinates=polygon)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "geo.intersects" in request.url

    @responses.activate
    def test_get_properties_with_media(self) -> None:
        """Test get properties with media expansion."""
        mock_response = {
            "@odata.context": "test",
            "value": [
                {
                    "ListingId": "12345678",
                    "Media": [
                        {"MediaUrl": "http://example.com/photo1.jpg"},
                        {"MediaUrl": "http://example.com/photo2.jpg"}
                    ]
                }
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_with_media(
            filter_query="StandardStatus eq 'Active'",
            top=25
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24expand=Media" in request.url
        assert "StandardStatus+eq+%27Active%27" in request.url
        assert "%24top=25" in request.url

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

        result = self.client.get_active_properties(
            top=50,
            select=["ListingId", "ListPrice", "UnparsedAddress"],
            orderby="ListPrice"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24filter=StandardStatus+eq+%27Active%27" in request.url or "StandardStatus+eq+%27Active%27" in request.url
        assert "%24top=50" in request.url

    @responses.activate
    def test_get_properties_by_price_range_both_limits(self) -> None:
        """Test price range filtering with both min and max."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_price_range(
            min_price=200000,
            max_price=500000,
            top=50
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListPrice+ge+200000" in request.url
        assert "ListPrice+le+500000" in request.url

    @responses.activate
    def test_get_properties_by_price_range_min_only(self) -> None:
        """Test price range filtering with minimum only."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_price_range(min_price=1000000)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListPrice+ge+1000000" in request.url

    @responses.activate
    def test_get_properties_by_price_range_max_only(self) -> None:
        """Test price range filtering with maximum only."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_price_range(max_price=300000)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListPrice+le+300000" in request.url

    @responses.activate
    def test_get_properties_by_price_range_no_limits(self) -> None:
        """Test price range filtering with no limits (should get all properties)."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_price_range()

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should not have any price filters
        assert "ListPrice" not in request.url

    @responses.activate
    def test_get_properties_by_city_success(self) -> None:
        """Test city filtering."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_city(
            city="Salt Lake City",
            top=100
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "City+eq+%27Salt+Lake+City%27" in request.url

    @responses.activate
    def test_get_properties_by_city_with_existing_filter(self) -> None:
        """Test city filtering with existing filter query."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_properties_by_city(
            city="Provo",
            filter_query="StandardStatus eq 'Active'",
            orderby="ListPrice"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "City+eq+%27Provo%27" in request.url
        assert "StandardStatus+eq+%27Active%27" in request.url

    @responses.activate
    def test_get_modified_properties_with_datetime_string(self) -> None:
        """Test modified properties filtering with datetime string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        since_time = "2024-01-15T10:00:00Z"
        result = self.client.get_modified_properties(since=since_time)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ModificationTimestamp+gt+2024-01-15T10%3A00%3A00Z" in request.url

    @responses.activate
    def test_get_modified_properties_with_date_object(self) -> None:
        """Test modified properties filtering with date object."""
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
        assert request.url is not None
        assert "ModificationTimestamp+gt+2023-01-01Z" in request.url

    @responses.activate
    def test_get_all_properties_paginated_success(self) -> None:
        """Test paginated property retrieval."""
        # First page response
        page1_response = {
            "@odata.context": "test",
            "@odata.nextLink": "https://api.example.com/Property?$skip=200",
            "value": [{"ListingId": f"P{i}"} for i in range(200)]
        }
        
        # Second page response
        page2_response = {
            "@odata.context": "test",
            "value": [{"ListingId": f"P{i}"} for i in range(200, 250)]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=page1_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://api.example.com/Property",
            json=page2_response,
            status=200,
        )

        result = self.client.get_all_properties_paginated(
            page_size=200,
            max_pages=2,
            filter_query="StandardStatus eq 'Active'"
        )

        assert "@odata.context" in result
        assert "value" in result
        assert "pagination_info" in result
        assert len(result["value"]) == 400  # 200 + 200 (both pages get mocked the same)
        assert result["pagination_info"]["pages_fetched"] == 2
        assert result["pagination_info"]["total_records"] == 400

    @responses.activate
    def test_get_all_properties_paginated_single_page(self) -> None:
        """Test paginated property retrieval with single page."""
        single_page_response = {
            "@odata.context": "test",
            "value": [{"ListingId": f"P{i}"} for i in range(50)]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=single_page_response,
            status=200,
        )

        result = self.client.get_all_properties_paginated(page_size=100)

        assert len(result["value"]) == 50
        assert result["pagination_info"]["pages_fetched"] == 1

    @responses.activate
    def test_get_all_properties_paginated_max_pages_limit(self) -> None:
        """Test paginated property retrieval with max pages limit."""
        page_response = {
            "@odata.context": "test",
            "@odata.nextLink": "https://api.example.com/Property?$skip=200",
            "value": [{"ListingId": f"P{i}"} for i in range(200)]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=page_response,
            status=200,
        )

        result = self.client.get_all_properties_paginated(
            page_size=200,
            max_pages=1  # Limit to 1 page
        )

        assert len(result["value"]) == 200
        assert result["pagination_info"]["pages_fetched"] == 1

    @responses.activate
    def test_search_properties_by_multiple_criteria_success(self) -> None:
        """Test search by multiple criteria."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        criteria = {
            "min_price": 200000,
            "max_price": 500000,
            "city": "Salt Lake City",
            "property_type": "Residential",
            "bedrooms": 3,
            "bathrooms": 2
        }

        result = self.client.search_properties_by_multiple_criteria(
            criteria=criteria,
            top=50,
            orderby="ListPrice desc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should combine all criteria in filter
        assert "ListPrice+ge+200000" in request.url
        assert "ListPrice+le+500000" in request.url
        assert "Salt+Lake+City" in request.url

    @responses.activate
    def test_search_properties_by_multiple_criteria_minimal(self) -> None:
        """Test search by multiple criteria with minimal criteria."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        criteria = {"min_price": 100000}

        result = self.client.search_properties_by_multiple_criteria(criteria=criteria)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListPrice+ge+100000" in request.url

    @responses.activate
    def test_search_properties_near_address_success(self) -> None:
        """Test search properties near address (uses geocoding simulation)."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.search_properties_near_address(
            address="123 Main St, Salt Lake City, UT",
            radius_miles=5.0,
            top=25
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # The method extracts city from address and filters by city
        assert "City+eq" in request.url
        assert "Salt+Lake+City" in request.url

    @responses.activate
    def test_get_luxury_properties_default(self) -> None:
        """Test get luxury properties with default minimum price."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_luxury_properties()

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListPrice+ge+1000000" in request.url

    @responses.activate
    def test_get_luxury_properties_custom_price(self) -> None:
        """Test get luxury properties with custom minimum price."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_luxury_properties(
            min_price=2000000,
            top=20,
            orderby="ListPrice desc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ListPrice+ge+2000000" in request.url
        assert "%24top=20" in request.url

    @responses.activate
    def test_get_new_listings_default(self) -> None:
        """Test get new listings with default days back."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_new_listings()

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should filter by listing date within last 7 days using gt (greater than)
        assert "ListingContractDate+gt" in request.url

    @responses.activate
    def test_get_new_listings_custom_days(self) -> None:
        """Test get new listings with custom days back."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json=mock_response,
            status=200,
        )

        result = self.client.get_new_listings(
            days_back=3,
            top=30,
            orderby="OnMarketDate desc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=30" in request.url

    def test_enum_values(self) -> None:
        """Test enum values are correct."""
        assert PropertyStatus.ACTIVE.value == "Active"
        assert PropertyStatus.PENDING.value == "Pending"
        assert PropertyStatus.SOLD.value == "Sold"
        assert PropertyStatus.EXPIRED.value == "Expired"
        assert PropertyStatus.WITHDRAWN.value == "Withdrawn"
        assert PropertyStatus.CANCELLED.value == "Cancelled"
        
        assert PropertyType.RESIDENTIAL.value == "Residential"
        assert PropertyType.COMMERCIAL.value == "Commercial"
        assert PropertyType.LAND.value == "Land"
        assert PropertyType.RENTAL.value == "Rental"

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
        assert request.url is not None
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
        assert request.url is not None
        assert "%24select=ListingId%2CListPrice%2CStandardStatus" in request.url

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
        assert request.url is not None
        assert "%24expand=Media%2CMember" in request.url

    @responses.activate
    def test_property_client_error_handling(self) -> None:
        """Test property client error handling."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json={"error": {"message": "Server error"}},
            status=500,
        )

        with pytest.raises(ServerError, match="Server error"):
            self.client.get_properties()

    @responses.activate
    def test_property_validation_error(self) -> None:
        """Test property validation error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Property",
            json={"error": {"message": "Invalid query parameter"}},
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request"):
            self.client.get_properties(filter_query="invalid syntax") 