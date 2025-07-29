"""Media client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class MediaType(Enum):
    """Media type options."""

    PHOTO = "Photo"
    VIDEO = "Video"
    DOCUMENT = "Document"
    VIRTUAL_TOUR = "VirtualTour"


class MediaCategory(Enum):
    """Media category options."""

    EXTERIOR = "Exterior"
    INTERIOR = "Interior"
    KITCHEN = "Kitchen"
    BATHROOM = "Bathroom"
    BEDROOM = "Bedroom"
    LIVING_ROOM = "LivingRoom"
    DINING_ROOM = "DiningRoom"
    GARAGE = "Garage"
    YARD = "Yard"
    POOL = "Pool"


class MediaClient(BaseClient):
    """Client for media (photos/videos) API endpoints.
    
    The Media resource contains property photos, videos, and other media files.
    Each media record is related to a Property through ResourceRecordKeyNumeric.
    Media items include URLs, ordering information, and descriptive metadata.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the media client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_media(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get media records with optional OData filtering.

        This method retrieves media (photo/video) information with full OData v4.0 query support.
        Commonly used to get photos for specific properties.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing media data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of media records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get media for a specific property
            media = client.media.get_media(
                filter_query="ResourceRecordKeyNumeric eq 1611952",
                orderby="Order asc",
                select=["MediaURL", "Order", "LongDescription"]
            )

            # Get first 10 photos only
            photos = client.media.get_media(
                filter_query="MediaType eq 'Photo'",
                top=10,
                orderby="Order asc"
            )

            # Get media with property info
            media_with_props = client.media.get_media(
                expand="Property",
                top=25
            )
            ```
        """
        params: Dict[str, Any] = {}

        if top is not None:
            # Enforce 200 record limit as per API specification
            params["$top"] = min(top, 200)
        if skip is not None:
            params["$skip"] = skip
        if filter_query is not None:
            params["$filter"] = filter_query
        if orderby is not None:
            params["$orderby"] = orderby
        if count is not None:
            params["$count"] = "true" if count else "false"

        if select is not None:
            if isinstance(select, list):
                params["$select"] = ",".join(select)
            else:
                params["$select"] = select

        if expand is not None:
            if isinstance(expand, list):
                params["$expand"] = ",".join(expand)
            else:
                params["$expand"] = expand

        return self.get("Media", params=params)

    def get_media_item(self, media_key: str) -> Dict[str, Any]:
        """Get media item by media key.

        Retrieves a single media record by its unique media key.
        This is the most efficient way to get detailed information about
        a specific photo, video, or document.

        Args:
            media_key: Media key to retrieve (unique identifier, often complex string)

        Returns:
            Dictionary containing media data for the specified item

        Raises:
            NotFoundError: If the media with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific media item by key
            media_item = client.media.get_media_item("1611952_050774e9ef920b479d8e37ff459daf14_2880536.jpg")
            
            print(f"Media URL: {media_item['MediaURL']}")
            print(f"Order: {media_item['Order']}")
            print(f"Description: {media_item.get('LongDescription', 'No description')}")
            ```
        """
        return self.get(f"Media('{media_key}')")

    def get_media_for_property(
        self,
        listing_key: Union[str, int],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get media for a specific property.

        Convenience method to retrieve all media (photos, videos, etc.) for a property.
        Uses ResourceRecordKeyNumeric to filter by property listing key.

        Args:
            listing_key: Property listing key (string or integer)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing media for the specified property

        Example:
            ```python
            # Get all photos for a property
            property_media = client.media.get_media_for_property(
                listing_key="1611952",
                orderby="Order asc"
            )
            
            # Get just photo URLs for a property
            photo_urls = client.media.get_media_for_property(
                listing_key=1611952,
                select=["MediaURL", "Order"],
                filter_query="MediaType eq 'Photo'"
            )
            
            # Get first 5 photos for a property
            first_photos = client.media.get_media_for_property(
                listing_key="1611952",
                top=5,
                orderby="Order asc"
            )
            ```
        """
        property_filter = f"ResourceRecordKeyNumeric eq {listing_key}"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{property_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = property_filter
            
        return self.get_media(**kwargs)

    def get_photos_for_property(
        self,
        listing_key: Union[str, int],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get photos only for a specific property.

        Convenience method to retrieve only photo media for a property,
        filtering out videos, documents, and other media types.

        Args:
            listing_key: Property listing key (string or integer)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing photos for the specified property

        Example:
            ```python
            # Get all photos for a property
            photos = client.media.get_photos_for_property(
                listing_key="1611952",
                orderby="Order asc"
            )
            
            # Get photo URLs only
            photo_urls = client.media.get_photos_for_property(
                listing_key="1611952",
                select=["MediaURL", "Order"],
                orderby="Order asc"
            )
            ```
        """
        photo_filter = f"ResourceRecordKeyNumeric eq {listing_key} and MediaType eq 'Photo'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{photo_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = photo_filter
            
        return self.get_media(**kwargs)

    def get_primary_photo(
        self,
        listing_key: Union[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Get the primary photo for a property.

        Convenience method to get the first/primary photo (Order = 1) for a property.
        Returns None if no photos are found.

        Args:
            listing_key: Property listing key (string or integer)

        Returns:
            Dictionary containing the primary photo data, or None if not found

        Example:
            ```python
            # Get primary photo for a property
            primary_photo = client.media.get_primary_photo("1611952")
            
            if primary_photo:
                print(f"Primary photo URL: {primary_photo['MediaURL']}")
            else:
                print("No primary photo found")
            ```
        """
        response = self.get_photos_for_property(
            listing_key=listing_key,
            filter_query="Order eq 1",
            top=1
        )
        
        if response.get('value'):
            return response['value'][0]
        return None

    def get_media_urls_for_property(
        self,
        listing_key: Union[str, int],
        media_type: Optional[str] = None
    ) -> List[str]:
        """Get just the media URLs for a property.

        Convenience method to extract just the MediaURL values for a property,
        returned as a simple list of URLs ordered by the Order field.

        Args:
            listing_key: Property listing key (string or integer)
            media_type: Optional media type filter ("Photo", "Video", etc.)

        Returns:
            List of media URLs ordered by Order field

        Example:
            ```python
            # Get all photo URLs for a property
            photo_urls = client.media.get_media_urls_for_property(
                listing_key="1611952",
                media_type="Photo"
            )
            
            # Get all media URLs (photos, videos, etc.)
            all_urls = client.media.get_media_urls_for_property("1611952")
            
            for url in photo_urls:
                print(f"Photo: {url}")
            ```
        """
        filter_parts = [f"ResourceRecordKeyNumeric eq {listing_key}"]
        
        if media_type:
            filter_parts.append(f"MediaType eq '{media_type}'")
            
        filter_query = " and ".join(filter_parts)
        
        response = self.get_media(
            filter_query=filter_query,
            select=["MediaURL"],
            orderby="Order asc",
            top=200  # Get up to the max limit
        )
        
        urls = []
        for item in response.get('value', []):
            if 'MediaURL' in item:
                urls.append(item['MediaURL'])
                
        return urls

    def get_media_by_category(
        self,
        listing_key: Union[str, int],
        category: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get media for a property filtered by category.

        Convenience method to filter media by category (e.g., "Interior", "Exterior").
        Useful for getting specific types of photos.

        Args:
            listing_key: Property listing key (string or integer)
            category: Media category to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing media for the specified category

        Example:
            ```python
            # Get exterior photos
            exterior_photos = client.media.get_media_by_category(
                listing_key="1611952",
                category="Exterior",
                orderby="Order asc"
            )
            
            # Get kitchen photos
            kitchen_photos = client.media.get_media_by_category(
                listing_key="1611952",
                category="Kitchen"
            )
            ```
        """
        category_filter = f"ResourceRecordKeyNumeric eq {listing_key} and MediaCategory eq '{category}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{category_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = category_filter
            
        return self.get_media(**kwargs)

    def get_media_with_property(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get media with their property information expanded.

        This is a convenience method that automatically expands the Property
        relationship to include property details in the response. More efficient
        than making separate requests for media and their properties.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing media data with expanded Property relationships

        Example:
            ```python
            # Get recent media with property info
            media_with_props = client.media.get_media_with_property(
                orderby="ModificationTimestamp desc",
                top=25
            )
            
            # Access property info for first media item
            first_media = media_with_props['value'][0]
            if 'Property' in first_media:
                property_info = first_media['Property']
                print(f"Photo for: {property_info['UnparsedAddress']}")
            ```
        """
        return self.get_media(expand="Property", **kwargs)

    def get_modified_media(
        self,
        since: Union[str, date, datetime],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get media modified since a specific date/time.

        Used for incremental data synchronization to get only media records
        that have been updated since the last sync. Essential for maintaining
        up-to-date photo and media information.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing media modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get media modified in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            updates = client.media.get_modified_media(
                since=cutoff_time
            )

            # Get media modified since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            updates = client.media.get_modified_media(
                since=yesterday,
                orderby="ModificationTimestamp desc"
            )
            ```
        """
        if isinstance(since, datetime):
            since_str = since.isoformat() + "Z"
        elif isinstance(since, date):
            since_str = since.isoformat() + "T00:00:00Z"
        else:
            since_str = since
            
        filter_query = f"ModificationTimestamp gt '{since_str}'"
        return self.get_media(filter_query=filter_query, **kwargs) 