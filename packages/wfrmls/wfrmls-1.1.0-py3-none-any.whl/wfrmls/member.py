"""Member client for WFRMLS API."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class MemberStatus(Enum):
    """Member status options."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class MemberType(Enum):
    """Member type options."""

    AGENT = "Agent"
    BROKER = "Broker"
    ASSISTANT = "Assistant"


class MemberClient(BaseClient):
    """Client for member (real estate agent) API endpoints.
    
    The Member resource contains information about real estate agents,
    brokers, and other MLS participants. This includes contact information,
    license details, and office affiliations.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the member client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_members(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get members with optional OData filtering.

        This method retrieves member (agent/broker) information with full OData v4.0 query support.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing member data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of member records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get first 10 active members
            members = client.member.get_members(
                top=10,
                filter_query="MemberStatus eq 'Active'"
            )

            # Get members with office info
            members = client.member.get_members(
                expand="Office",
                top=50
            )

            # Get members with specific fields only
            members = client.member.get_members(
                select=["MemberKey", "MemberFirstName", "MemberLastName", "MemberEmail"],
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

        return self.get("Member", params=params)

    def get_member(self, member_key: str) -> Dict[str, Any]:
        """Get member by member key.

        Retrieves a single member record by its unique member key.
        This is the most efficient way to get detailed information about
        a specific agent or broker.

        Args:
            member_key: Member key to retrieve (unique identifier)

        Returns:
            Dictionary containing member data for the specified member

        Raises:
            NotFoundError: If the member with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific member by key
            member = client.member.get_member("12345")
            
            print(f"Agent: {member['MemberFirstName']} {member['MemberLastName']}")
            print(f"Email: {member['MemberEmail']}")
            ```
        """
        return self.get(f"Member('{member_key}')")

    def get_active_members(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get members with Active status.

        Convenience method to retrieve only active members.
        This filters out inactive, suspended, or terminated agents/brokers.

        Args:
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing active member listings

        Example:
            ```python
            # Get all active members
            active_members = client.member.get_active_members(top=100)

            # Get active members with specific fields
            active_members = client.member.get_active_members(
                select=["MemberKey", "MemberFirstName", "MemberLastName", "MemberPhone"],
                orderby="MemberLastName"
            )
            ```
        """
        return self.get_members(filter_query="MemberStatus eq 'Active'", **kwargs)

    def get_members_by_office(
        self,
        office_key: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get members affiliated with a specific office.

        Convenience method to filter members by their office affiliation.
        Useful for getting all agents/brokers in a particular brokerage.

        Args:
            office_key: Office key to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing members affiliated with the specified office

        Example:
            ```python
            # Get all members in a specific office
            office_members = client.member.get_members_by_office(
                office_key="12345",
                top=100
            )
            
            # Get active members in an office
            active_office_members = client.member.get_members_by_office(
                office_key="12345",
                filter_query="MemberStatus eq 'Active'",
                orderby="MemberLastName"
            )
            ```
        """
        office_filter = f"OfficeKey eq '{office_key}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{office_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = office_filter
            
        return self.get_members(**kwargs)

    def search_members_by_name(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Search members by first name and/or last name.

        Convenience method to find agents/brokers by name using partial matching.
        Uses OData string functions for flexible name searching.

        Args:
            first_name: First name to search for (partial matching)
            last_name: Last name to search for (partial matching)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing members matching the name criteria

        Example:
            ```python
            # Search by last name only
            smiths = client.member.search_members_by_name(
                last_name="Smith",
                top=50
            )

            # Search by first and last name
            johns = client.member.search_members_by_name(
                first_name="John",
                last_name="Smith"
            )
            ```
        """
        filters = []
        
        if first_name is not None:
            filters.append(f"contains(MemberFirstName, '{first_name}')")
        if last_name is not None:
            filters.append(f"contains(MemberLastName, '{last_name}')")
            
        if not filters:
            # No name filters, just get all members
            return self.get_members(**kwargs)
            
        filter_query = " and ".join(filters)
        return self.get_members(filter_query=filter_query, **kwargs)

    def get_members_with_office(
        self,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get members with their office information expanded.

        This is a convenience method that automatically expands the Office
        relationship to include office details in the response. More efficient
        than making separate requests for members and their offices.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing member data with expanded Office relationships

        Example:
            ```python
            # Get active members with office info
            members = client.member.get_members_with_office(
                filter_query="MemberStatus eq 'Active'",
                top=25
            )
            
            # Access office info for first member
            first_member = members['value'][0]
            if 'Office' in first_member:
                office_info = first_member['Office']
                print(f"Member works at: {office_info['OfficeName']}")
            ```
        """
        return self.get_members(expand="Office", **kwargs)

    def get_modified_members(
        self,
        since: Union[str, date],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get members modified since a specific date/time.

        Used for incremental data synchronization to get only member records
        that have been updated since the last sync. Essential for maintaining
        up-to-date agent/broker information.

        Args:
            since: ISO format datetime string or date object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing members modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get members modified in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            updates = client.member.get_modified_members(
                since=cutoff_time.isoformat() + "Z"
            )

            # Get members modified since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            updates = client.member.get_modified_members(
                since=yesterday.isoformat() + "Z"
            )
            ```
        """
        if isinstance(since, date):
            since_str = since.isoformat() + "Z"
        else:
            since_str = since
            
        filter_query = f"ModificationTimestamp gt {since_str}"
        return self.get_members(filter_query=filter_query, **kwargs) 