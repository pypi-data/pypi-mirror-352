"""Tests for WFRMLS Media module."""

from datetime import date, datetime, timedelta
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from wfrmls.exceptions import WFRMLSError
from wfrmls.media import MediaCategory, MediaClient, MediaType


class TestMediaType:
    """Test suite for MediaType enum."""

    def test_media_type_values(self) -> None:
        """Test MediaType enum values."""
        assert MediaType.PHOTO.value == "Photo"
        assert MediaType.VIDEO.value == "Video"
        assert MediaType.DOCUMENT.value == "Document"
        assert MediaType.VIRTUAL_TOUR.value == "VirtualTour"


class TestMediaCategory:
    """Test suite for MediaCategory enum."""

    def test_media_category_values(self) -> None:
        """Test MediaCategory enum values."""
        assert MediaCategory.EXTERIOR.value == "Exterior"
        assert MediaCategory.INTERIOR.value == "Interior"
        assert MediaCategory.KITCHEN.value == "Kitchen"
        assert MediaCategory.BATHROOM.value == "Bathroom"
        assert MediaCategory.BEDROOM.value == "Bedroom"
        assert MediaCategory.LIVING_ROOM.value == "LivingRoom"
        assert MediaCategory.DINING_ROOM.value == "DiningRoom"
        assert MediaCategory.GARAGE.value == "Garage"
        assert MediaCategory.YARD.value == "Yard"
        assert MediaCategory.POOL.value == "Pool"


class TestMediaClient:
    """Test suite for MediaClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = MediaClient(bearer_token="test_token")

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_basic(self, mock_get: Mock) -> None:
        """Test basic get_media functionality."""
        mock_response: Dict[str, Any] = {
            "value": [
                {
                    "MediaKey": "123_photo.jpg",
                    "MediaURL": "https://example.com/photo.jpg",
                    "Order": 1,
                    "MediaType": "Photo",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_media()

        mock_get.assert_called_once_with("Media", params={})
        assert result == mock_response

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_with_all_params(self, mock_get: Mock) -> None:
        """Test get_media with all parameters."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get.return_value = mock_response

        result = self.client.get_media(
            top=50,
            skip=10,
            filter_query="ResourceRecordKeyNumeric eq 12345",
            select=["MediaURL", "Order"],
            orderby="Order asc",
            expand=["Property"],
            count=True,
        )

        expected_params = {
            "$top": 50,
            "$skip": 10,
            "$filter": "ResourceRecordKeyNumeric eq 12345",
            "$select": "MediaURL,Order",
            "$orderby": "Order asc",
            "$expand": "Property",
            "$count": "true",
        }

        mock_get.assert_called_once_with("Media", params=expected_params)

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_top_limit_enforcement(self, mock_get: Mock) -> None:
        """Test that top parameter is limited to 200."""
        mock_get.return_value = {"value": []}

        self.client.get_media(top=300)

        expected_params = {"$top": 200}
        mock_get.assert_called_once_with("Media", params=expected_params)

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_select_string(self, mock_get: Mock) -> None:
        """Test get_media with select as string."""
        mock_get.return_value = {"value": []}

        self.client.get_media(select="MediaURL,Order")

        expected_params = {"$select": "MediaURL,Order"}
        mock_get.assert_called_once_with("Media", params=expected_params)

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_expand_string(self, mock_get: Mock) -> None:
        """Test get_media with expand as string."""
        mock_get.return_value = {"value": []}

        self.client.get_media(expand="Property,Member")

        expected_params = {"$expand": "Property,Member"}
        mock_get.assert_called_once_with("Media", params=expected_params)

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_count_false(self, mock_get: Mock) -> None:
        """Test get_media with count=False."""
        mock_get.return_value = {"value": []}

        self.client.get_media(count=False)

        expected_params = {"$count": "false"}
        mock_get.assert_called_once_with("Media", params=expected_params)

    @patch("wfrmls.media.MediaClient.get")
    def test_get_media_item(self, mock_get: Mock) -> None:
        """Test get_media_item functionality."""
        media_key = "123_photo.jpg"
        mock_response: Dict[str, Any] = {
            "MediaKey": media_key,
            "MediaURL": "https://example.com/photo.jpg",
            "Order": 1,
        }
        mock_get.return_value = mock_response

        result = self.client.get_media_item(media_key)

        mock_get.assert_called_once_with(f"Media('{media_key}')")
        assert result == mock_response

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_for_property_string_key(self, mock_get_media: Mock) -> None:
        """Test get_media_for_property with string listing key."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_media_for_property(
            listing_key="12345", orderby="Order asc"
        )

        mock_get_media.assert_called_once_with(
            filter_query="ResourceRecordKeyNumeric eq 12345", orderby="Order asc"
        )

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_for_property_int_key(self, mock_get_media: Mock) -> None:
        """Test get_media_for_property with integer listing key."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_media_for_property(listing_key=12345)

        mock_get_media.assert_called_once_with(
            filter_query="ResourceRecordKeyNumeric eq 12345"
        )

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_for_property_with_existing_filter(
        self, mock_get_media: Mock
    ) -> None:
        """Test get_media_for_property with existing filter_query."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_media_for_property(
            listing_key="12345", filter_query="MediaType eq 'Photo'"
        )

        expected_filter = "ResourceRecordKeyNumeric eq 12345 and MediaType eq 'Photo'"
        mock_get_media.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_photos_for_property(self, mock_get_media: Mock) -> None:
        """Test get_photos_for_property functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_photos_for_property(
            listing_key="12345", orderby="Order asc"
        )

        expected_filter = "ResourceRecordKeyNumeric eq 12345 and MediaType eq 'Photo'"
        mock_get_media.assert_called_once_with(
            filter_query=expected_filter, orderby="Order asc"
        )

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_photos_for_property_with_existing_filter(
        self, mock_get_media: Mock
    ) -> None:
        """Test get_photos_for_property with existing filter_query."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_photos_for_property(
            listing_key="12345", filter_query="Order le 5"
        )

        expected_filter = (
            "ResourceRecordKeyNumeric eq 12345 and MediaType eq 'Photo' and Order le 5"
        )
        mock_get_media.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.media.MediaClient.get_photos_for_property")
    def test_get_primary_photo_found(self, mock_get_photos: Mock) -> None:
        """Test get_primary_photo when photo is found."""
        primary_photo = {
            "MediaKey": "123_primary.jpg",
            "MediaURL": "https://example.com/primary.jpg",
            "Order": 1,
        }
        mock_get_photos.return_value = {"value": [primary_photo]}

        result = self.client.get_primary_photo("12345")

        mock_get_photos.assert_called_once_with(
            listing_key="12345", filter_query="Order eq 1", top=1
        )
        assert result == primary_photo

    @patch("wfrmls.media.MediaClient.get_photos_for_property")
    def test_get_primary_photo_not_found(self, mock_get_photos: Mock) -> None:
        """Test get_primary_photo when no photo is found."""
        mock_get_photos.return_value = {"value": []}

        result = self.client.get_primary_photo("12345")

        assert result is None

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_urls_for_property_photos_only(
        self, mock_get_media: Mock
    ) -> None:
        """Test get_media_urls_for_property with photo filter."""
        mock_response: Dict[str, Any] = {
            "value": [
                {"MediaURL": "https://example.com/photo1.jpg"},
                {"MediaURL": "https://example.com/photo2.jpg"},
                {"MediaURL": "https://example.com/photo3.jpg"},
            ]
        }
        mock_get_media.return_value = mock_response

        result = self.client.get_media_urls_for_property(
            listing_key="12345", media_type="Photo"
        )

        expected_filter = "ResourceRecordKeyNumeric eq 12345 and MediaType eq 'Photo'"
        mock_get_media.assert_called_once_with(
            filter_query=expected_filter,
            select=["MediaURL"],
            orderby="Order asc",
            top=200,
        )

        expected_urls = [
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg",
            "https://example.com/photo3.jpg",
        ]
        assert result == expected_urls

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_urls_for_property_all_media(self, mock_get_media: Mock) -> None:
        """Test get_media_urls_for_property without media type filter."""
        mock_response: Dict[str, Any] = {
            "value": [
                {"MediaURL": "https://example.com/photo.jpg"},
                {"MediaURL": "https://example.com/video.mp4"},
                {},  # Missing MediaURL
            ]
        }
        mock_get_media.return_value = mock_response

        result = self.client.get_media_urls_for_property(listing_key=12345)

        expected_filter = "ResourceRecordKeyNumeric eq 12345"
        mock_get_media.assert_called_once_with(
            filter_query=expected_filter,
            select=["MediaURL"],
            orderby="Order asc",
            top=200,
        )

        expected_urls = [
            "https://example.com/photo.jpg",
            "https://example.com/video.mp4",
        ]
        assert result == expected_urls

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_by_category(self, mock_get_media: Mock) -> None:
        """Test get_media_by_category functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_media_by_category(
            listing_key="12345", category="Kitchen", orderby="Order asc"
        )

        expected_filter = (
            "ResourceRecordKeyNumeric eq 12345 and MediaCategory eq 'Kitchen'"
        )
        mock_get_media.assert_called_once_with(
            filter_query=expected_filter, orderby="Order asc"
        )

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_by_category_with_existing_filter(
        self, mock_get_media: Mock
    ) -> None:
        """Test get_media_by_category with existing filter_query."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_media_by_category(
            listing_key="12345", category="Exterior", filter_query="Order le 10"
        )

        expected_filter = "ResourceRecordKeyNumeric eq 12345 and MediaCategory eq 'Exterior' and Order le 10"
        mock_get_media.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_media_with_property(self, mock_get_media: Mock) -> None:
        """Test get_media_with_property functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        result = self.client.get_media_with_property(
            orderby="ModificationTimestamp desc", top=25
        )

        mock_get_media.assert_called_once_with(
            expand="Property", orderby="ModificationTimestamp desc", top=25
        )

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_modified_media_datetime(self, mock_get_media: Mock) -> None:
        """Test get_modified_media with datetime object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        since_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = self.client.get_modified_media(
            since=since_datetime, orderby="ModificationTimestamp desc"
        )

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_media.assert_called_once_with(
            filter_query=expected_filter, orderby="ModificationTimestamp desc"
        )

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_modified_media_date(self, mock_get_media: Mock) -> None:
        """Test get_modified_media with date object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        since_date = date(2024, 1, 1)
        result = self.client.get_modified_media(since=since_date)

        expected_filter = "ModificationTimestamp gt '2024-01-01T00:00:00Z'"
        mock_get_media.assert_called_once_with(filter_query=expected_filter)

    @patch("wfrmls.media.MediaClient.get_media")
    def test_get_modified_media_string(self, mock_get_media: Mock) -> None:
        """Test get_modified_media with string."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_media.return_value = mock_response

        since_string = "2024-01-01T12:00:00Z"
        result = self.client.get_modified_media(since=since_string)

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_media.assert_called_once_with(filter_query=expected_filter)

    def test_init_default_params(self) -> None:
        """Test MediaClient initialization with default parameters."""
        client = MediaClient()
        # Test that it doesn't raise an exception and creates properly
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")

    def test_init_with_params(self) -> None:
        """Test MediaClient initialization with custom parameters."""
        client = MediaClient(
            bearer_token="custom_token", base_url="https://custom.api.com"
        )
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")
