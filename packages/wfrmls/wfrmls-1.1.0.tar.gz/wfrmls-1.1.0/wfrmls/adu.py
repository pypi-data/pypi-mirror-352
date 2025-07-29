"""Adu client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class AduType(Enum):
    """ADU type options."""

    DETACHED = "Detached"
    ATTACHED = "Attached"
    GARAGE_CONVERSION = "Garage Conversion"
    BASEMENT = "Basement"
    INTERIOR = "Interior"


class AduStatus(Enum):
    """ADU status options."""

    EXISTING = "Existing"
    PERMITTED = "Permitted"
    PLANNED = "Planned"
    UNDER_CONSTRUCTION = "Under Construction"


class AduClient(BaseClient):
    """Client for Accessory Dwelling Unit (ADU) API endpoints.
    
    The Adu resource contains information about accessory dwelling units
    associated with properties. ADUs are secondary housing units on single-family
    residential lots and are important for housing density and rental income potential.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the ADU client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_adus(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get ADU data with optional OData filtering.

        This method retrieves ADU information with full OData v4.0 query support.
        Provides information about accessory dwelling units and their characteristics.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing ADU data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of ADU records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get all ADUs
            adus = client.adu.get_adus()
            
            # Get ADUs for existing units
            adus = client.adu.get_adus(
                filter_query="AduStatus eq 'Existing'",
                orderby="CreatedDate desc"
            )

            # Get ADUs with property information
            adus = client.adu.get_adus(
                expand="Property",
                select=["AduKey", "ListingKey", "AduType", "AduStatus"],
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

        return self.get("Adu", params=params)

    def get_adu(self, adu_key: str) -> Dict[str, Any]:
        """Get ADU by ADU key.

        Retrieves a single ADU record by its unique key.
        This is the most efficient way to get detailed information about
        a specific accessory dwelling unit.

        Args:
            adu_key: ADU key to retrieve (unique identifier)

        Returns:
            Dictionary containing ADU data for the specified record

        Raises:
            NotFoundError: If the ADU with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific ADU by key
            adu = client.adu.get_adu("ADU123456")
            
            print(f"ADU Type: {adu['AduType']}")
            print(f"Status: {adu['AduStatus']}")
            print(f"Square Feet: {adu.get('SquareFeet', 'Unknown')}")
            print(f"Bedrooms: {adu.get('Bedrooms', 'Unknown')}")
            ```
        """
        return self.get(f"Adu('{adu_key}')")

    def get_adus_for_property(
        self,
        listing_key: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get ADUs for a specific property.

        Convenience method to retrieve all ADUs associated with a property.
        Useful for understanding accessory dwelling unit potential for a property.

        Args:
            listing_key: Property listing key to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing ADUs for the specified property

        Example:
            ```python
            # Get ADUs for a property
            property_adus = client.adu.get_adus_for_property(
                listing_key="1611952",
                orderby="AduType asc"
            )
            
            # Get existing ADUs for a property
            existing_adus = client.adu.get_adus_for_property(
                listing_key="1611952",
                filter_query="AduStatus eq 'Existing'"
            )
            ```
        """
        property_filter = f"ListingKey eq '{listing_key}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{property_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = property_filter
            
        return self.get_adus(**kwargs)

    def get_adus_by_type(
        self,
        adu_type: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get ADUs by type.

        Convenience method to filter ADUs by type.
        Useful for finding specific types of accessory dwelling units.

        Args:
            adu_type: ADU type to filter by (e.g., "Detached", "Attached")
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing ADUs of the specified type

        Example:
            ```python
            # Get all detached ADUs
            detached_adus = client.adu.get_adus_by_type(
                adu_type="Detached",
                expand="Property"
            )
            
            # Get garage conversion ADUs
            garage_adus = client.adu.get_adus_by_type("Garage Conversion")
            ```
        """
        type_filter = f"AduType eq '{adu_type}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{type_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = type_filter
            
        return self.get_adus(**kwargs)

    def get_adus_by_status(
        self,
        adu_status: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get ADUs by status.

        Convenience method to filter ADUs by status.
        Useful for finding ADUs in specific development stages.

        Args:
            adu_status: ADU status to filter by (e.g., "Existing", "Permitted")
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing ADUs with the specified status

        Example:
            ```python
            # Get existing ADUs
            existing_adus = client.adu.get_adus_by_status(
                adu_status="Existing",
                orderby="CreatedDate desc"
            )
            
            # Get planned ADUs
            planned_adus = client.adu.get_adus_by_status("Planned")
            ```
        """
        status_filter = f"AduStatus eq '{adu_status}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{status_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = status_filter
            
        return self.get_adus(**kwargs)

    def get_existing_adus(self, **kwargs: Any) -> Dict[str, Any]:
        """Get existing ADUs.

        Convenience method to retrieve only existing/built ADUs.
        Excludes planned, permitted, or under-construction units.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing existing ADUs

        Example:
            ```python
            # Get all existing ADUs
            existing_adus = client.adu.get_existing_adus(
                expand="Property",
                orderby="CreatedDate desc"
            )
            ```
        """
        return self.get_adus_by_status("Existing", **kwargs)

    def get_permitted_adus(self, **kwargs: Any) -> Dict[str, Any]:
        """Get permitted ADUs.

        Convenience method to retrieve ADUs that have permits but may not
        be built yet. Useful for understanding development pipeline.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing permitted ADUs

        Example:
            ```python
            # Get all permitted ADUs
            permitted_adus = client.adu.get_permitted_adus()
            ```
        """
        return self.get_adus_by_status("Permitted", **kwargs)

    def get_adus_with_property(self, **kwargs: Any) -> Dict[str, Any]:
        """Get ADUs with their property information expanded.

        This is a convenience method that automatically expands property
        relationships to include property details in the response.
        More efficient than making separate requests for ADUs and properties.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing ADU data with expanded property relationships

        Example:
            ```python
            # Get ADUs with property information
            adus_with_props = client.adu.get_adus_with_property(
                top=25
            )
            
            # Access property info for first ADU
            first_adu = adus_with_props['value'][0]
            if 'Property' in first_adu:
                property_info = first_adu['Property']
                print(f"ADU on property: {property_info['UnparsedAddress']}")
            ```
        """
        return self.get_adus(expand="Property", **kwargs)

    def get_modified_adus(
        self,
        since: Union[str, date, datetime],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get ADUs modified since a specific date/time.

        Used for incremental data synchronization to get only ADU records
        that have been updated since the last sync. Useful for maintaining
        up-to-date accessory dwelling unit information.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing ADUs modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get ADUs modified in last week
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            updates = client.adu.get_modified_adus(
                since=cutoff_time
            )

            # Get ADUs modified since a specific date
            updates = client.adu.get_modified_adus(
                since="2023-01-01T00:00:00Z",
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
        return self.get_adus(filter_query=filter_query, **kwargs) 