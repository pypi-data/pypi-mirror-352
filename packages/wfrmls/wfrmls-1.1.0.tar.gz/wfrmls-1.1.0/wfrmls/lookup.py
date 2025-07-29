"""Lookup client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class LookupClient(BaseClient):
    """Client for lookup table data API endpoints.
    
    The Lookup resource contains enumeration values and reference data used
    throughout the MLS system. This includes property types, status values,
    and other standardized lookup values.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the lookup client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_lookups(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get lookup data with optional OData filtering.

        This method retrieves lookup table data with full OData v4.0 query support.
        Provides access to enumeration values and reference data used in the system.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing lookup data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of lookup records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get all lookup data
            lookups = client.lookup.get_lookups()
            
            # Get lookups for a specific resource
            lookups = client.lookup.get_lookups(
                filter_query="LookupName eq 'PropertyType'",
                orderby="DisplayOrder asc"
            )

            # Get lookup values with specific fields
            lookups = client.lookup.get_lookups(
                select=["LookupKey", "LookupName", "LookupValue", "StandardLookupValue"],
                top=100
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

        return self.get("Lookup", params=params)

    def get_lookup(self, lookup_key: str) -> Dict[str, Any]:
        """Get lookup by lookup key.

        Retrieves a single lookup record by its unique key.
        This is the most efficient way to get detailed information about
        a specific lookup value.

        Args:
            lookup_key: Lookup key to retrieve (unique identifier)

        Returns:
            Dictionary containing lookup data for the specified record

        Raises:
            NotFoundError: If the lookup with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific lookup by key
            lookup = client.lookup.get_lookup("PROP_TYPE_RESIDENTIAL")
            
            print(f"Lookup Name: {lookup['LookupName']}")
            print(f"Value: {lookup['LookupValue']}")
            print(f"Standard Value: {lookup.get('StandardLookupValue', 'N/A')}")
            ```
        """
        return self.get(f"Lookup('{lookup_key}')")

    def get_lookups_by_name(
        self,
        lookup_name: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get lookups by lookup name.

        Convenience method to retrieve all lookup values for a specific lookup name.
        Useful for getting all values for enumeration types like PropertyType, 
        PropertyStatus, etc.

        Args:
            lookup_name: Lookup name to filter by (e.g., "PropertyType", "PropertyStatus")
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing lookups for the specified name

        Example:
            ```python
            # Get all property type lookups
            property_types = client.lookup.get_lookups_by_name(
                lookup_name="PropertyType",
                orderby="DisplayOrder asc"
            )
            
            # Get all property status lookups
            statuses = client.lookup.get_lookups_by_name("PropertyStatus")
            ```
        """
        name_filter = f"LookupName eq '{lookup_name}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{name_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = name_filter
            
        return self.get_lookups(**kwargs)

    def get_property_type_lookups(self, **kwargs: Any) -> Dict[str, Any]:
        """Get property type lookup values.

        Convenience method to retrieve all property type enumeration values.
        Useful for understanding available property types in the system.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing property type lookup values

        Example:
            ```python
            # Get all property types
            property_types = client.lookup.get_property_type_lookups(
                orderby="DisplayOrder asc"
            )
            
            for prop_type in property_types.get('value', []):
                print(f"Property Type: {prop_type['LookupValue']}")
            ```
        """
        return self.get_lookups_by_name("PropertyType", **kwargs)

    def get_property_status_lookups(self, **kwargs: Any) -> Dict[str, Any]:
        """Get property status lookup values.

        Convenience method to retrieve all property status enumeration values.
        Useful for understanding available property statuses in the system.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing property status lookup values

        Example:
            ```python
            # Get all property statuses
            statuses = client.lookup.get_property_status_lookups()
            
            for status in statuses.get('value', []):
                print(f"Status: {status['LookupValue']}")
            ```
        """
        return self.get_lookups_by_name("PropertyStatus", **kwargs)

    def get_standard_lookups(self, **kwargs: Any) -> Dict[str, Any]:
        """Get standard RESO lookup values.

        Convenience method to filter for standard RESO-defined lookup values.
        These are the core lookup values defined by the RESO standard.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing standard RESO lookup values

        Example:
            ```python
            # Get all standard lookups
            standard_lookups = client.lookup.get_standard_lookups()
            
            for lookup in standard_lookups.get('value', []):
                print(f"Standard Lookup: {lookup['StandardLookupValue']}")
            ```
        """
        # Filter for lookups that have a StandardLookupValue (RESO standard lookups)
        standard_filter = "StandardLookupValue ne null"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{standard_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = standard_filter
            
        return self.get_lookups(**kwargs)

    def get_active_lookups(self, **kwargs: Any) -> Dict[str, Any]:
        """Get active lookup values.

        Convenience method to filter for active/enabled lookup values.
        Excludes deprecated or disabled lookup entries.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing active lookup values

        Example:
            ```python
            # Get all active lookups
            active_lookups = client.lookup.get_active_lookups(
                orderby="LookupName asc, DisplayOrder asc"
            )
            ```
        """
        # Filter for active lookups (assuming IsActive field exists)
        active_filter = "IsActive eq true"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{active_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = active_filter
            
        return self.get_lookups(**kwargs)

    def get_lookup_names(self) -> List[str]:
        """Get list of unique lookup names.

        Convenience method to get a list of all available lookup names in the system.
        Useful for discovering what lookup types are available.

        Returns:
            List of unique lookup names

        Example:
            ```python
            # Get all available lookup names
            lookup_names = client.lookup.get_lookup_names()
            
            for name in lookup_names:
                print(f"Available lookup: {name}")
            ```
        """
        response = self.get_lookups(
            select=["LookupName"],
            orderby="LookupName asc"
        )
        
        names = set()
        for item in response.get('value', []):
            if 'LookupName' in item:
                names.add(item['LookupName'])
                
        return sorted(list(names))

    def get_modified_lookups(
        self,
        since: Union[str, date, datetime],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get lookups modified since a specific date/time.

        Used for incremental data synchronization to get only lookup records
        that have been updated since the last sync. Useful for maintaining
        up-to-date lookup values and enumeration data.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing lookups modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get lookups modified in last month
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            updates = client.lookup.get_modified_lookups(
                since=cutoff_time
            )

            # Get lookups modified since a specific date
            updates = client.lookup.get_modified_lookups(
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
        return self.get_lookups(filter_query=filter_query, **kwargs) 