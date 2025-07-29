"""Property client for WFRMLS API."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class PropertyStatus(Enum):
    """Property status options."""

    ACTIVE = "Active"
    PENDING = "Pending"
    SOLD = "Sold"
    EXPIRED = "Expired"
    WITHDRAWN = "Withdrawn"
    CANCELLED = "Cancelled"


class PropertyType(Enum):
    """Property type options."""

    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    LAND = "Land"
    RENTAL = "Rental"


class PropertyClient(BaseClient):
    """Client for property API endpoints.
    
    The Property resource is the primary resource in the WFRMLS API, containing
    real estate listing data including property details, pricing, and location
    information. This client provides access to all property-related endpoints
    with comprehensive OData query support.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the property client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_properties(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get properties with optional OData filtering.

        This method retrieves property listings with full OData v4.0 query support.
        It's the primary method for accessing property data in the WFRMLS system.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets,
                prefer NextLink pagination instead
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing property data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of property records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get first 10 active properties
            properties = client.property.get_properties(
                top=10,
                filter_query="StandardStatus eq 'Active'"
            )

            # Get properties with photos and agent info
            properties = client.property.get_properties(
                expand=["Media", "Member"],
                top=50
            )

            # Get properties in price range with sorting
            properties = client.property.get_properties(
                filter_query="ListPrice ge 200000 and ListPrice le 500000",
                orderby="ListPrice desc",
                top=100
            )

            # Get properties with specific fields only
            properties = client.property.get_properties(
                select=["ListingId", "ListPrice", "StandardStatus", "City"],
                top=50
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

        return self.get("Property", params=params)

    def get_property(self, listing_id: str) -> Dict[str, Any]:
        """Get property by listing ID.

        Retrieves a single property record by its unique listing ID.
        This is the most efficient way to get detailed information about
        a specific property.

        Args:
            listing_id: Listing ID to retrieve (ResourceRecordKey)

        Returns:
            Dictionary containing property data for the specified listing

        Raises:
            NotFoundError: If the property with the given ID is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific property by listing ID
            property = client.property.get_property("12345678")
            
            print(f"Property: {property['ListPrice']}")
            print(f"Address: {property['UnparsedAddress']}")
            ```
        """
        return self.get(f"Property('{listing_id}')")

    def search_properties_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float,
        additional_filters: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search properties within a radius of given coordinates.

        Uses geospatial queries to find properties within a specified distance
        from a center point. This is ideal for location-based property searches.

        Args:
            latitude: Latitude coordinate for center point
            longitude: Longitude coordinate for center point
            radius_miles: Search radius in miles
            additional_filters: Additional OData filter query to combine with geo filter
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing property data within the specified radius

        Raises:
            ValidationError: If coordinates are invalid
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Find properties within 10 miles of Salt Lake City
            properties = client.property.search_properties_by_radius(
                latitude=40.7608,
                longitude=-111.8910,
                radius_miles=10,
                additional_filters="StandardStatus eq 'Active'",
                top=50
            )

            # Find expensive properties near downtown
            properties = client.property.search_properties_by_radius(
                latitude=40.7608,
                longitude=-111.8910,
                radius_miles=5,
                additional_filters="ListPrice ge 500000 and StandardStatus eq 'Active'",
                orderby="ListPrice desc"
            )
            ```
        """
        geo_filter = f"geo.distance(Latitude, Longitude, {latitude}, {longitude}) le {radius_miles}"
        
        if additional_filters:
            filter_query = f"{geo_filter} and {additional_filters}"
        else:
            filter_query = geo_filter
            
        return self.get_properties(filter_query=filter_query, **kwargs)

    def search_properties_by_polygon(
        self,
        polygon_coordinates: List[Dict[str, float]],
        additional_filters: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search properties within a polygon area.

        Uses geospatial polygon intersection to find properties within
        a defined boundary. Useful for searching within specific
        neighborhoods, districts, or custom geographic areas.

        Args:
            polygon_coordinates: List of coordinate dicts with 'lat' and 'lng' keys.
                Must have at least 3 points and should be closed (first == last).
            additional_filters: Additional OData filter query to combine with geo filter
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing property data within the polygon

        Raises:
            ValidationError: If polygon coordinates are invalid
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Define polygon around downtown area
            polygon = [
                {"lat": 40.7608, "lng": -111.8910},
                {"lat": 40.7708, "lng": -111.8810},
                {"lat": 40.7508, "lng": -111.8710},
                {"lat": 40.7608, "lng": -111.8910}  # Close polygon
            ]
            
            properties = client.property.search_properties_by_polygon(
                polygon_coordinates=polygon,
                additional_filters="PropertyType eq 'Residential'",
                top=100
            )
            ```
        """
        # Build polygon string for geo.intersects function
        coords_str = ",".join([f"{coord['lat']} {coord['lng']}" for coord in polygon_coordinates])
        geo_filter = f"geo.intersects(Latitude, Longitude, geography'POLYGON(({coords_str}))')"
        
        if additional_filters:
            filter_query = f"{geo_filter} and {additional_filters}"
        else:
            filter_query = geo_filter
            
        return self.get_properties(filter_query=filter_query, **kwargs)

    def get_properties_with_media(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get properties with their associated media/photos.

        This is a convenience method that automatically expands the Media
        relationship to include property photos in the response. More efficient
        than making separate requests for properties and their media.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing property data with expanded Media relationships

        Example:
            ```python
            # Get active properties with photos
            properties = client.property.get_properties_with_media(
                filter_query="StandardStatus eq 'Active'",
                top=25
            )
            
            # Access photos for first property
            first_property = properties['value'][0]
            if 'Media' in first_property:
                photos = first_property['Media']
                print(f"Property has {len(photos)} photos")
            ```
        """
        return self.get_properties(expand="Media", **kwargs)

    def get_active_properties(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get properties with Active status.

        Convenience method to retrieve only active property listings.
        This is one of the most common queries for real estate applications.

        Args:
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing active property listings

        Example:
            ```python
            # Get all active properties
            active_properties = client.property.get_active_properties(top=100)

            # Get active properties with specific fields
            active_properties = client.property.get_active_properties(
                select=["ListingId", "ListPrice", "UnparsedAddress"],
                orderby="ListPrice"
            )
            ```
        """
        return self.get_properties(filter_query="StandardStatus eq 'Active'", **kwargs)

    def get_properties_by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get properties within a price range.

        Convenience method to filter properties by listing price range.
        Commonly used for buyer searches and market analysis.

        Args:
            min_price: Minimum listing price (inclusive)
            max_price: Maximum listing price (inclusive)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing properties within the price range

        Example:
            ```python
            # Properties between $200K and $500K
            properties = client.property.get_properties_by_price_range(
                min_price=200000,
                max_price=500000,
                top=50
            )

            # Properties under $300K
            properties = client.property.get_properties_by_price_range(
                max_price=300000
            )

            # Properties over $1M
            properties = client.property.get_properties_by_price_range(
                min_price=1000000
            )
            ```
        """
        filters = []
        
        if min_price is not None:
            filters.append(f"ListPrice ge {min_price}")
        if max_price is not None:
            filters.append(f"ListPrice le {max_price}")
            
        if not filters:
            # No price filters, just get all properties
            return self.get_properties(**kwargs)
            
        filter_query = " and ".join(filters)
        return self.get_properties(filter_query=filter_query, **kwargs)

    def get_properties_by_city(
        self,
        city: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get properties in a specific city.

        Convenience method to filter properties by city name.
        Useful for location-specific searches.

        Args:
            city: City name to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing properties in the specified city

        Example:
            ```python
            # Get properties in Salt Lake City
            properties = client.property.get_properties_by_city(
                city="Salt Lake City",
                top=100
            )
            
            # Get active properties in Provo
            properties = client.property.get_properties_by_city(
                city="Provo",
                filter_query="StandardStatus eq 'Active'",
                orderby="ListPrice"
            )
            ```
        """
        city_filter = f"City eq '{city}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{city_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = city_filter
            
        return self.get_properties(**kwargs)

    def get_modified_properties(
        self,
        since: Union[str, date],
        **kwargs
    ) -> Dict[str, Any]:
        """Get properties modified since a specific date/time.

        Used for incremental data synchronization to get only properties
        that have been updated since the last sync. Essential for maintaining
        up-to-date property data.

        Args:
            since: ISO format datetime string or date object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing properties modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get properties modified in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            updates = client.property.get_modified_properties(
                since=cutoff_time.isoformat() + "Z"
            )

            # Get properties modified since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            updates = client.property.get_modified_properties(
                since=yesterday.isoformat() + "Z"
            )
            ```
        """
        if isinstance(since, date):
            since_str = since.isoformat() + "Z"
        else:
            since_str = since
            
        filter_query = f"ModificationTimestamp gt {since_str}"
        return self.get_properties(filter_query=filter_query, **kwargs)

    def get_all_properties_paginated(
        self,
        page_size: int = 200,
        max_pages: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get all properties using efficient pagination.

        This method automatically handles pagination to retrieve large datasets
        efficiently. Uses the recommended approach of fetching in chunks rather
        than using large skip values.

        Args:
            page_size: Number of records per request (max 200, default 200)
            max_pages: Maximum number of pages to fetch (None for all)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing all paginated results combined:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - value: Combined list of all property records
                - pagination_info: Metadata about pagination

        Example:
            ```python
            # Get all active properties in chunks
            all_properties = client.property.get_all_properties_paginated(
                filter_query="StandardStatus eq 'Active'",
                page_size=200,
                max_pages=10  # Limit to first 2000 records
            )
            
            print(f"Retrieved {len(all_properties['value'])} properties")
            print(f"Pages fetched: {all_properties['pagination_info']['pages_fetched']}")
            ```
        """
        all_results = []
        pages_fetched = 0
        current_skip = 0
        page_size = min(page_size, 200)  # Enforce API limit
        
        # Store original top parameter
        original_top = kwargs.get('top')
        
        while True:
            # Set pagination parameters
            kwargs['top'] = page_size
            kwargs['skip'] = current_skip
            
            # Fetch current page
            try:
                response = self.get_properties(**kwargs)
                pages_fetched += 1
                
                # Extract results
                page_results = response.get('value', [])
                if not page_results:
                    break  # No more data
                    
                all_results.extend(page_results)
                
                # Check if we should continue
                if max_pages and pages_fetched >= max_pages:
                    break
                    
                if len(page_results) < page_size:
                    break  # Last page (partial results)
                    
                # Prepare for next page
                current_skip += page_size
                
            except Exception:
                # If pagination fails, return what we have so far
                break
        
        # Build combined response
        combined_response = {
            "@odata.context": response.get("@odata.context", "") if 'response' in locals() else "",
            "value": all_results,
            "pagination_info": {
                "pages_fetched": pages_fetched,
                "total_records": len(all_results),
                "page_size": page_size,
                "last_skip": current_skip
            }
        }
        
        # Add count if it was in the last response
        if 'response' in locals() and '@odata.count' in response:
            combined_response['@odata.count'] = response['@odata.count']
            
        return combined_response

    def search_properties_by_multiple_criteria(
        self,
        criteria: Dict[str, Any],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search properties using multiple criteria with intelligent filtering.

        Convenience method that builds complex OData filters from a criteria dictionary.
        Supports common search patterns used in real estate applications.

        Args:
            criteria: Dictionary of search criteria:
                - status: Property status (Active, Pending, etc.)
                - min_price: Minimum listing price
                - max_price: Maximum listing price
                - city: City name
                - property_type: Property type (Residential, Commercial, etc.)
                - min_bedrooms: Minimum number of bedrooms
                - max_bedrooms: Maximum number of bedrooms
                - min_bathrooms: Minimum number of bathrooms
                - max_bathrooms: Maximum number of bathrooms
                - min_sqft: Minimum square footage
                - max_sqft: Maximum square footage
                - zip_code: Postal code
                - school_district: School district name
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing filtered property results

        Example:
            ```python
            # Complex property search
            criteria = {
                'status': 'Active',
                'min_price': 300000,
                'max_price': 600000,
                'city': 'Salt Lake City',
                'property_type': 'Residential',
                'min_bedrooms': 3,
                'min_bathrooms': 2,
                'min_sqft': 1500
            }
            
            properties = client.property.search_properties_by_multiple_criteria(
                criteria=criteria,
                top=50,
                orderby='ListPrice'
            )
            ```
        """
        filters = []
        
        # Status filter
        if 'status' in criteria and criteria['status']:
            filters.append(f"StandardStatus eq '{criteria['status']}'")
            
        # Price range filters
        if 'min_price' in criteria and criteria['min_price']:
            filters.append(f"ListPrice ge {criteria['min_price']}")
        if 'max_price' in criteria and criteria['max_price']:
            filters.append(f"ListPrice le {criteria['max_price']}")
            
        # Location filters
        if 'city' in criteria and criteria['city']:
            filters.append(f"City eq '{criteria['city']}'")
        if 'zip_code' in criteria and criteria['zip_code']:
            filters.append(f"PostalCode eq '{criteria['zip_code']}'")
        if 'school_district' in criteria and criteria['school_district']:
            filters.append(f"SchoolDistrict eq '{criteria['school_district']}'")
            
        # Property type filter
        if 'property_type' in criteria and criteria['property_type']:
            filters.append(f"PropertyType eq '{criteria['property_type']}'")
            
        # Bedroom filters
        if 'min_bedrooms' in criteria and criteria['min_bedrooms']:
            filters.append(f"BedroomsTotal ge {criteria['min_bedrooms']}")
        if 'max_bedrooms' in criteria and criteria['max_bedrooms']:
            filters.append(f"BedroomsTotal le {criteria['max_bedrooms']}")
            
        # Bathroom filters  
        if 'min_bathrooms' in criteria and criteria['min_bathrooms']:
            filters.append(f"BathroomsTotalInteger ge {criteria['min_bathrooms']}")
        if 'max_bathrooms' in criteria and criteria['max_bathrooms']:
            filters.append(f"BathroomsTotalInteger le {criteria['max_bathrooms']}")
            
        # Square footage filters
        if 'min_sqft' in criteria and criteria['min_sqft']:
            filters.append(f"LivingArea ge {criteria['min_sqft']}")
        if 'max_sqft' in criteria and criteria['max_sqft']:
            filters.append(f"LivingArea le {criteria['max_sqft']}")
        
        # Combine all filters
        if filters:
            filter_query = " and ".join(filters)
            # If additional filter_query provided, combine them
            existing_filter = kwargs.get('filter_query')
            if existing_filter:
                kwargs['filter_query'] = f"{filter_query} and {existing_filter}"
            else:
                kwargs['filter_query'] = filter_query
                
        return self.get_properties(**kwargs)

    def search_properties_near_address(
        self,
        address: str,
        radius_miles: float = 5.0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search properties near a specific address.

        This method would typically geocode the address to coordinates and then
        search within a radius. For now, it provides a framework for address-based
        searching that can be enhanced with geocoding services.

        Args:
            address: Street address to search near
            radius_miles: Search radius in miles (default: 5.0)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing properties near the address

        Note:
            This is a framework method. In production, you would integrate with
            a geocoding service to convert the address to coordinates first.

        Example:
            ```python
            # Search near a specific address
            properties = client.property.search_properties_near_address(
                address="123 Main St, Salt Lake City, UT",
                radius_miles=2.0,
                additional_filters="StandardStatus eq 'Active'"
            )
            ```
        """
        # This is a framework method that would need geocoding integration
        # For now, we'll search by address components if the address is structured
        
        # Basic implementation: try to extract city from address
        address_parts = address.split(',')
        if len(address_parts) >= 2:
            potential_city = address_parts[-2].strip()  # City is usually second to last
            
            # Search by city as a fallback
            city_filter = f"City eq '{potential_city}'"
            
            existing_filter = kwargs.get('filter_query')
            if existing_filter:
                kwargs['filter_query'] = f"{city_filter} and {existing_filter}"
            else:
                kwargs['filter_query'] = city_filter
                
            return self.get_properties(**kwargs)
        else:
            # If address can't be parsed, return empty results
            return {
                "@odata.context": "",
                "value": [],
                "error": "Address could not be parsed. Please provide city coordinates for radius search."
            }

    def get_luxury_properties(
        self,
        min_price: float = 1000000,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get luxury properties above a price threshold.

        Convenience method for finding high-end properties with additional
        luxury-focused filtering options.

        Args:
            min_price: Minimum price for luxury properties (default: $1M)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing luxury property listings

        Example:
            ```python
            # Get luxury properties over $2M
            luxury_homes = client.property.get_luxury_properties(
                min_price=2000000,
                top=25,
                orderby="ListPrice desc"
            )
            ```
        """
        filter_query = f"ListPrice ge {min_price} and StandardStatus eq 'Active'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{filter_query} and {existing_filter}"
        else:
            kwargs['filter_query'] = filter_query
            
        return self.get_properties(**kwargs)

    def get_new_listings(
        self,
        days_back: int = 7,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get properties listed within the last N days.

        Useful for finding fresh inventory and new market entries.

        Args:
            days_back: Number of days to look back (default: 7)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing recently listed properties

        Example:
            ```python
            # Get properties listed in last 3 days
            new_listings = client.property.get_new_listings(
                days_back=3,
                filter_query="StandardStatus eq 'Active'",
                orderby="ListingContractDate desc"
            )
            ```
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        cutoff_str = cutoff_date.isoformat() + "Z"
        
        filter_query = f"ListingContractDate gt {cutoff_str}"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{filter_query} and {existing_filter}"
        else:
            kwargs['filter_query'] = filter_query
            
        return self.get_properties(**kwargs) 