"""Office client for WFRMLS API."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class OfficeStatus(Enum):
    """Office status options."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class OfficeType(Enum):
    """Office type options."""

    MAIN = "Main"
    BRANCH = "Branch"
    FRANCHISE = "Franchise"


class OfficeClient(BaseClient):
    """Client for office (real estate brokerage) API endpoints.
    
    The Office resource contains information about real estate brokerages,
    including contact information, addresses, and licensing details.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the office client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_offices(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get offices with optional OData filtering.

        This method retrieves office (brokerage) information with full OData v4.0 query support.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing office data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of office records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get first 10 active offices
            offices = client.office.get_offices(
                top=10,
                filter_query="OfficeStatus eq 'Active'"
            )

            # Get offices with member info
            offices = client.office.get_offices(
                expand="Member",
                top=50
            )

            # Get offices with specific fields only
            offices = client.office.get_offices(
                select=["OfficeKey", "OfficeName", "OfficePhone", "OfficeEmail"],
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

        return self.get("Office", params=params)

    def get_office(self, office_key: str) -> Dict[str, Any]:
        """Get office by office key.

        Retrieves a single office record by its unique office key.
        This is the most efficient way to get detailed information about
        a specific brokerage.

        Args:
            office_key: Office key to retrieve (unique identifier)

        Returns:
            Dictionary containing office data for the specified office

        Raises:
            NotFoundError: If the office with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific office by key
            office = client.office.get_office("12345")
            
            print(f"Office: {office['OfficeName']}")
            print(f"Phone: {office['OfficePhone']}")
            print(f"Address: {office['OfficeAddress']}")
            ```
        """
        return self.get(f"Office('{office_key}')")

    def get_active_offices(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get offices with Active status.

        Convenience method to retrieve only active offices.
        This filters out inactive, suspended, or terminated brokerages.

        Args:
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing active office listings

        Example:
            ```python
            # Get all active offices
            active_offices = client.office.get_active_offices(top=100)

            # Get active offices with specific fields
            active_offices = client.office.get_active_offices(
                select=["OfficeKey", "OfficeName", "OfficePhone", "OfficeCity"],
                orderby="OfficeName"
            )
            ```
        """
        return self.get_offices(filter_query="OfficeStatus eq 'Active'", **kwargs)

    def get_offices_by_city(
        self,
        city: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get offices in a specific city.

        Convenience method to filter offices by city name.
        Useful for location-specific brokerage searches.

        Args:
            city: City name to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing offices in the specified city

        Example:
            ```python
            # Get offices in Salt Lake City
            offices = client.office.get_offices_by_city(
                city="Salt Lake City",
                top=100
            )
            
            # Get active offices in Provo
            offices = client.office.get_offices_by_city(
                city="Provo",
                filter_query="OfficeStatus eq 'Active'",
                orderby="OfficeName"
            )
            ```
        """
        city_filter = f"OfficeCity eq '{city}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{city_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = city_filter
            
        return self.get_offices(**kwargs)

    def search_offices_by_name(
        self,
        name: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search offices by name using partial matching.

        Convenience method to find brokerages by name using partial matching.
        Uses OData string functions for flexible name searching.

        Args:
            name: Office name to search for (partial matching)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing offices matching the name criteria

        Example:
            ```python
            # Search for offices with "Realty" in the name
            realty_offices = client.office.search_offices_by_name(
                name="Realty",
                top=50
            )

            # Search for Coldwell Banker offices
            cb_offices = client.office.search_offices_by_name(
                name="Coldwell Banker"
            )
            ```
        """
        filter_query = f"contains(OfficeName, '{name}')"
        return self.get_offices(filter_query=filter_query, **kwargs)

    def get_offices_with_members(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get offices with their member information expanded.

        This is a convenience method that automatically expands the Member
        relationship to include agent/broker details in the response. More efficient
        than making separate requests for offices and their members.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing office data with expanded Member relationships

        Example:
            ```python
            # Get active offices with member info
            offices = client.office.get_offices_with_members(
                filter_query="OfficeStatus eq 'Active'",
                top=25
            )
            
            # Access members for first office
            first_office = offices['value'][0]
            if 'Member' in first_office:
                members = first_office['Member']
                print(f"Office has {len(members)} members")
            ```
        """
        return self.get_offices(expand="Member", **kwargs)

    def get_offices_by_zipcode(
        self,
        zipcode: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get offices in a specific ZIP code.

        Convenience method to filter offices by postal code.
        Useful for geographic-based brokerage searches.

        Args:
            zipcode: ZIP/postal code to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing offices in the specified ZIP code

        Example:
            ```python
            # Get offices in ZIP code 84101 (downtown Salt Lake City)
            offices = client.office.get_offices_by_zipcode(
                zipcode="84101",
                top=50
            )
            ```
        """
        zipcode_filter = f"OfficePostalCode eq '{zipcode}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{zipcode_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = zipcode_filter
            
        return self.get_offices(**kwargs)

    def get_modified_offices(
        self,
        since: Union[str, date],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get offices modified since a specific date/time.

        Used for incremental data synchronization to get only office records
        that have been updated since the last sync. Essential for maintaining
        up-to-date brokerage information.

        Args:
            since: ISO format datetime string or date object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing offices modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get offices modified in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            updates = client.office.get_modified_offices(
                since=cutoff_time.isoformat() + "Z"
            )

            # Get offices modified since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            updates = client.office.get_modified_offices(
                since=yesterday.isoformat() + "Z"
            )
            ```
        """
        if isinstance(since, date):
            since_str = since.isoformat() + "Z"
        else:
            since_str = since
            
        filter_query = f"ModificationTimestamp gt {since_str}"
        return self.get_offices(filter_query=filter_query, **kwargs) 