"""Tests for WFRMLS Analytics module."""

import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from wfrmls.analytics import WFRMLSAnalytics
from wfrmls.exceptions import WFRMLSError


class TestWFRMLSAnalytics:
    """Test suite for WFRMLSAnalytics class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.analytics = WFRMLSAnalytics(self.mock_client)

    def test_init(self) -> None:
        """Test analytics initialization."""
        assert self.analytics.client == self.mock_client

    def test_get_market_summary_basic(self) -> None:
        """Test basic market summary functionality."""
        # Mock property data
        mock_active_response = {
            "value": [
                {
                    "ListPrice": 500000,
                    "ListingContractDate": "2024-01-01T00:00:00Z",
                    "PropertyType": "Residential",
                },
                {
                    "ListPrice": 600000,
                    "ListingContractDate": "2024-01-02T00:00:00Z",
                    "PropertyType": "Residential",
                },
            ]
        }

        mock_new_response = {
            "value": [
                {
                    "ListPrice": 550000,
                    "ListingContractDate": "2024-01-15T00:00:00Z",
                    "PropertyType": "Residential",
                }
            ]
        }

        self.mock_client.property.get_properties.side_effect = [
            mock_active_response,
            mock_new_response,
        ]

        result = self.analytics.get_market_summary(
            city="Salt Lake City", days_back=30, property_type="Residential"
        )

        assert result["market_area"] == "Salt Lake City"
        assert result["property_type"] == "Residential"
        assert result["inventory"]["active_listings"] == 2
        assert result["inventory"]["new_listings"] == 1
        assert result["pricing"]["average_price"] == 550000
        assert result["pricing"]["median_price"] == 550000

    def test_get_market_summary_no_filters(self) -> None:
        """Test market summary without city or property type filters."""
        mock_response = {
            "value": [
                {"ListPrice": 300000, "ListingContractDate": "2024-01-01T00:00:00Z"}
            ]
        }

        self.mock_client.property.get_properties.side_effect = [
            mock_response,
            {"value": []},
        ]

        result = self.analytics.get_market_summary(days_back=30)

        assert result["market_area"] == "All Areas"
        assert result["property_type"] == "All Types"
        assert result["inventory"]["active_listings"] == 1

    def test_get_market_summary_empty_data(self) -> None:
        """Test market summary with no properties."""
        self.mock_client.property.get_properties.side_effect = [
            {"value": []},
            {"value": []},
        ]

        result = self.analytics.get_market_summary()

        assert result["inventory"]["active_listings"] == 0
        assert result["pricing"]["average_price"] == 0
        assert result["activity"]["avg_days_on_market"] == 0

    def test_get_market_summary_invalid_dates(self) -> None:
        """Test market summary with invalid date formats."""
        mock_response = {
            "value": [
                {"ListPrice": 400000, "ListingContractDate": "invalid-date"},
                {"ListPrice": 500000, "ListingContractDate": None},
            ]
        }

        self.mock_client.property.get_properties.side_effect = [
            mock_response,
            {"value": []},
        ]

        result = self.analytics.get_market_summary()

        assert result["inventory"]["active_listings"] == 2
        assert result["activity"]["avg_days_on_market"] == 0

    def test_get_market_summary_exception(self) -> None:
        """Test market summary error handling."""
        self.mock_client.property.get_properties.side_effect = Exception("API Error")

        result = self.analytics.get_market_summary()

        assert "error" in result
        assert "Failed to generate market summary" in result["error"]

    def test_analyze_price_trends_basic(self) -> None:
        """Test basic price trend analysis."""
        mock_response = {
            "value": [
                {
                    "ListPrice": 300000,
                    "BedroomsTotal": 3,
                    "BathroomsTotalInteger": 2,
                    "LivingArea": 1500,
                    "ListingContractDate": "2024-01-01T00:00:00Z",
                },
                {
                    "ListPrice": 500000,
                    "BedroomsTotal": 4,
                    "BathroomsTotalInteger": 3,
                    "LivingArea": 2000,
                    "ListingContractDate": "2024-01-02T00:00:00Z",
                },
                {
                    "ListPrice": 700000,
                    "BedroomsTotal": 5,
                    "BathroomsTotalInteger": 4,
                    "LivingArea": 2500,
                    "ListingContractDate": "2024-01-03T00:00:00Z",
                },
            ]
        }

        self.mock_client.property.get_properties.return_value = mock_response

        result = self.analytics.analyze_price_trends(
            city="Park City", property_type="Residential", price_segments=3
        )

        assert result["market_area"] == "Park City"
        assert result["properties_analyzed"] == 3
        assert len(result["price_segments"]) == 3
        assert result["overall_pricing"]["average_price"] == 500000
        assert (
            abs(result["overall_pricing"]["avg_price_per_sqft"] - 243.33) < 0.1
        )  # Average of price/sqft

        # Check segment names for 3 segments
        segment_names = [seg["name"] for seg in result["price_segments"]]
        assert "Budget" in segment_names
        assert "Mid-Range" in segment_names
        assert "Luxury" in segment_names

    def test_analyze_price_trends_many_segments(self) -> None:
        """Test price trend analysis with many segments."""
        mock_response = {
            "value": [
                {"ListPrice": i * 100000, "LivingArea": 1000 + i * 100}
                for i in range(1, 11)  # 10 properties
            ]
        }

        self.mock_client.property.get_properties.return_value = mock_response

        result = self.analytics.analyze_price_trends(price_segments=5)

        assert len(result["price_segments"]) == 5
        # Check that segments have generic names for >3 segments
        segment_names = [seg["name"] for seg in result["price_segments"]]
        assert any("Segment" in name for name in segment_names)

    def test_analyze_price_trends_no_data(self) -> None:
        """Test price trend analysis with no valid data."""
        mock_response = {
            "value": [
                {"ListPrice": 0},  # Invalid price
                {"ListPrice": None},  # No price
                {},  # No price field
            ]
        }

        self.mock_client.property.get_properties.return_value = mock_response

        result = self.analytics.analyze_price_trends()

        assert "error" in result
        assert "Failed to analyze price trends" in result["error"]

    def test_analyze_price_trends_exception(self) -> None:
        """Test price trend analysis error handling."""
        self.mock_client.property.get_properties.side_effect = Exception("API Error")

        result = self.analytics.analyze_price_trends()

        assert "error" in result
        assert "Failed to analyze price trends" in result["error"]

    def test_generate_agent_performance_report_basic(self) -> None:
        """Test basic agent performance report."""
        mock_listings = {
            "value": [
                {
                    "ListingId": "1",
                    "ListPrice": 500000,
                    "StandardStatus": "Active",
                    "ListingContractDate": "2024-01-01T00:00:00Z",
                    "Member": {"MemberKey": "AGENT1"},
                },
                {
                    "ListingId": "2",
                    "ListPrice": 600000,
                    "StandardStatus": "Pending",
                    "ListingContractDate": "2024-01-02T00:00:00Z",
                    "Member": {"MemberKey": "AGENT1"},
                },
                {
                    "ListingId": "3",
                    "ListPrice": 700000,
                    "StandardStatus": "Active",
                    "ListingContractDate": "2024-01-03T00:00:00Z",
                    "Member": {"MemberKey": "AGENT2"},
                },
            ]
        }

        mock_members = {
            "value": [
                {
                    "MemberKey": "AGENT1",
                    "MemberFullName": "John Smith",
                    "MemberEmail": "john@example.com",
                    "OfficeKey": "OFF1",
                },
                {
                    "MemberKey": "AGENT2",
                    "MemberFullName": "Jane Doe",
                    "MemberEmail": "jane@example.com",
                    "OfficeKey": "OFF2",
                },
            ]
        }

        self.mock_client.property.get_properties.return_value = mock_listings
        self.mock_client.member.get_members.return_value = mock_members

        result = self.analytics.generate_agent_performance_report(
            days_back=90, min_listings=1
        )

        assert result["total_agents_analyzed"] == 2
        assert result["total_listings_analyzed"] == 3

        # Check top agents by listings
        top_by_listings = result["top_agents"]["by_listings"]
        assert len(top_by_listings) == 2
        assert top_by_listings[0]["name"] == "John Smith"
        assert top_by_listings[0]["listing_count"] == 2
        assert top_by_listings[0]["active_listings"] == 1
        assert top_by_listings[0]["pending_listings"] == 1

    def test_generate_agent_performance_report_min_listings_filter(self) -> None:
        """Test agent performance report with minimum listings filter."""
        mock_listings = {
            "value": [
                {
                    "ListingId": "1",
                    "ListPrice": 500000,
                    "Member": {"MemberKey": "AGENT1"},
                },
                {
                    "ListingId": "2",
                    "ListPrice": 600000,
                    "Member": {"MemberKey": "AGENT2"},
                },
            ]
        }

        mock_members = {
            "value": [
                {"MemberKey": "AGENT1", "MemberFullName": "John Smith"},
                {"MemberKey": "AGENT2", "MemberFullName": "Jane Doe"},
            ]
        }

        self.mock_client.property.get_properties.return_value = mock_listings
        self.mock_client.member.get_members.return_value = mock_members

        result = self.analytics.generate_agent_performance_report(min_listings=5)

        # No agents should qualify with min_listings=5
        assert result["total_agents_analyzed"] == 0

    def test_generate_agent_performance_report_invalid_member_data(self) -> None:
        """Test agent performance report with invalid member data."""
        mock_listings = {
            "value": [
                {
                    "ListingId": "1",
                    "ListPrice": 500000,
                    "Member": None,  # Invalid member
                },
                {
                    "ListingId": "2",
                    "ListPrice": 600000,
                    "Member": {"MemberKey": "NONEXISTENT"},  # Member not in lookup
                },
                {
                    "ListingId": "3",
                    "ListPrice": 700000,
                    "Member": "invalid_format",  # Wrong format
                },
            ]
        }

        self.mock_client.property.get_properties.return_value = mock_listings
        self.mock_client.member.get_members.return_value = {"value": []}

        result = self.analytics.generate_agent_performance_report()

        assert result["total_agents_analyzed"] == 0

    def test_generate_agent_performance_report_exception(self) -> None:
        """Test agent performance report error handling."""
        self.mock_client.property.get_properties.side_effect = Exception("API Error")

        result = self.analytics.generate_agent_performance_report()

        assert "error" in result
        assert "Failed to generate agent performance report" in result["error"]

    def test_get_data_quality_report_basic(self) -> None:
        """Test basic data quality report."""
        mock_properties = {
            "value": [
                {
                    "ListingId": "1",
                    "ListPrice": 500000,
                    "UnparsedAddress": "123 Main St",
                    "City": "Salt Lake City",
                    "BedroomsTotal": 3,
                    "LivingArea": 1500,
                },
                {
                    "ListingId": "2",
                    "ListPrice": None,  # Missing price
                    "UnparsedAddress": "",  # Empty address
                    "City": "Park City",
                    "BedroomsTotal": None,  # Missing bedrooms
                    "LivingArea": 2000,
                },
            ]
        }

        mock_members = {"value": [{"MemberKey": "M1", "MemberFullName": "John Smith"}]}
        mock_offices = {"value": [{"OfficeKey": "O1", "OfficeName": "ABC Realty"}]}

        self.mock_client.property.get_properties.return_value = mock_properties
        self.mock_client.member.get_members.return_value = mock_members
        self.mock_client.office.get_offices.return_value = mock_offices

        result = self.analytics.get_data_quality_report()

        assert "property_quality" in result
        assert "member_quality" in result
        assert "overall_quality_score" in result
        assert "recommendations" in result
        assert "issues" in result

        # Check that issues and recommendations are identified
        property_quality = result["property_quality"]
        assert "completeness_score" in property_quality
        assert "missing_data" in property_quality

    def test_get_data_quality_report_exception(self) -> None:
        """Test data quality report error handling."""
        self.mock_client.property.get_properties.side_effect = Exception("API Error")

        result = self.analytics.get_data_quality_report()

        assert "error" in result
        assert "Failed to generate data quality report" in result["error"]

    def test_get_data_quality_report_empty_data(self) -> None:
        """Test data quality report with empty responses."""
        self.mock_client.property.get_properties.return_value = {"value": []}
        self.mock_client.member.get_members.return_value = {"value": []}

        result = self.analytics.get_data_quality_report()

        # When data is empty, check that we get a reasonable response
        assert "timestamp" in result
