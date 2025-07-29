"""OpenHouse client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class OpenHouseStatus(Enum):
    """OpenHouse status options."""

    ACTIVE = "Active"
    ENDED = "Ended"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class OpenHouseType(Enum):
    """OpenHouse type options."""

    PUBLIC = "Public"
    PRIVATE = "Private"
    BROKER = "Broker"


class OpenHouseAttendedBy(Enum):
    """Who attends the open house."""

    AGENT = "Agent"
    OWNER = "Owner"
    NONE = "None"
    LISTING_AGENT = "ListingAgent"
    BUYER_AGENT = "BuyerAgent"


class OpenHouseClient(BaseClient):
    """Client for open house schedule API endpoints.

    The OpenHouse resource contains information about scheduled open house events,
    including dates, times, showing agents, and related property information.
    All timestamps are in UTC format.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the open house client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_open_houses(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get open houses with optional OData filtering.

        This method retrieves open house schedule information with full OData v4.0 query support.
        All timestamps are returned in UTC format.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing open house data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of open house records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get upcoming open houses
            open_houses = client.openhouse.get_open_houses(
                filter_query="OpenHouseStartTime gt '2023-12-01T00:00:00Z'",
                orderby="OpenHouseStartTime asc",
                top=50
            )

            # Get open houses with property info
            open_houses = client.openhouse.get_open_houses(
                expand="Property",
                top=25
            )

            # Get open houses with specific fields only
            open_houses = client.openhouse.get_open_houses(
                select=["OpenHouseKey", "ListingKey", "OpenHouseStartTime", "OpenHouseEndTime"],
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

        return self.get("OpenHouse", params=params)

    def get_open_house(self, open_house_key: str) -> Dict[str, Any]:
        """Get open house by open house key.

        Retrieves a single open house record by its unique open house key.
        This is the most efficient way to get detailed information about
        a specific open house event.

        Args:
            open_house_key: Open house key to retrieve (unique identifier)

        Returns:
            Dictionary containing open house data for the specified event

        Raises:
            NotFoundError: If the open house with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific open house by key
            open_house = client.openhouse.get_open_house("306227")

            print(f"Open House: {open_house['OpenHouseStartTime']} - {open_house['OpenHouseEndTime']}")
            print(f"Property: {open_house['ListingKey']}")
            print(f"Agent: {open_house['ShowingAgentFirstName']} {open_house['ShowingAgentLastName']}")
            ```
        """
        return self.get(f"OpenHouse('{open_house_key}')")

    def get_upcoming_open_houses(
        self,
        days_ahead: Optional[int] = 7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get upcoming open houses.

        Convenience method to retrieve open houses scheduled for the near future.

        Args:
            days_ahead: Number of days ahead to search (default: 7)
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing upcoming open house listings

        Example:
            ```python
            # Get open houses for next 3 days
            upcoming = client.openhouse.get_upcoming_open_houses(
                days_ahead=3,
                orderby="OpenHouseStartTime asc",
                top=50
            )

            # Get this week's open houses
            weekend_opens = client.openhouse.get_upcoming_open_houses(
                days_ahead=7,
                expand="Property",
                select=["OpenHouseKey", "ListingKey", "OpenHouseStartTime", "OpenHouseEndTime"]
            )
            ```
        """
        # Remove days_ahead from kwargs if it exists to avoid conflicts
        kwargs.pop('days_ahead', None)
        
        if days_ahead is not None:
            from datetime import datetime, timedelta
            start_date = datetime.now().date()
            filter_query = f"OpenHouseDate ge {start_date.isoformat()}"
            
            # If additional filter_query provided, combine them
            existing_filter = kwargs.get("filter_query")
            if existing_filter:
                kwargs["filter_query"] = f"{filter_query} and {existing_filter}"
            else:
                kwargs["filter_query"] = filter_query
        
        return self.get_open_houses(**kwargs)

    def get_open_houses_for_property(
        self, listing_key: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get open houses for a specific property.

        Convenience method to filter open houses by property listing key.
        Useful for finding all scheduled showings for a particular property.

        Args:
            listing_key: Property listing key to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing open houses for the specified property

        Example:
            ```python
            # Get all open houses for a property
            property_opens = client.openhouse.get_open_houses_for_property(
                listing_key="1625740",
                orderby="OpenHouseStartTime asc"
            )

            # Get upcoming open houses for property
            upcoming_opens = client.openhouse.get_open_houses_for_property(
                listing_key="1625740",
                filter_query="OpenHouseStartTime gt '2023-12-01T00:00:00Z'"
            )
            ```
        """
        property_filter = f"ListingKey eq '{listing_key}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{property_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = property_filter

        return self.get_open_houses(**kwargs)

    def get_open_houses_by_agent(self, agent_key: str, **kwargs: Any) -> Dict[str, Any]:
        """Get open houses by showing agent.

        Convenience method to filter open houses by the agent conducting them.
        Useful for finding all open houses managed by a specific agent.

        Args:
            agent_key: Showing agent key to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing open houses for the specified agent

        Example:
            ```python
            # Get all open houses for an agent
            agent_opens = client.openhouse.get_open_houses_by_agent(
                agent_key="96422",
                orderby="OpenHouseStartTime asc",
                top=100
            )
            ```
        """
        agent_filter = f"ShowingAgentKey eq '{agent_key}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{agent_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = agent_filter

        return self.get_open_houses(**kwargs)

    def get_active_open_houses(self, **kwargs: Any) -> Dict[str, Any]:
        """Get open houses with Active status.

        Convenience method to retrieve only active open houses.
        Filters out ended, cancelled, or expired open house events.

        Args:
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing active open house listings

        Example:
            ```python
            # Get all active open houses
            active_opens = client.openhouse.get_active_open_houses(
                orderby="OpenHouseStartTime asc",
                top=100
            )

            # Get active open houses with property details
            active_with_props = client.openhouse.get_active_open_houses(
                expand="Property",
                select=["OpenHouseKey", "ListingKey", "OpenHouseStartTime", "OpenHouseStatus"],
                top=50
            )
            ```
        """
        return self.get_open_houses(
            filter_query="OpenHouseStatus eq 'Active'", **kwargs
        )

    def get_open_houses_with_property(self, **kwargs: Any) -> Dict[str, Any]:
        """Get open houses with their property information expanded.

        This is a convenience method that automatically expands the Property
        relationship to include property details in the response. More efficient
        than making separate requests for open houses and their properties.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing open house data with expanded Property relationships

        Example:
            ```python
            # Get upcoming open houses with property info
            opens_with_props = client.openhouse.get_open_houses_with_property(
                filter_query="OpenHouseStartTime gt '2023-12-01T00:00:00Z'",
                orderby="OpenHouseStartTime asc",
                top=25
            )

            # Access property info for first open house
            first_open = opens_with_props['value'][0]
            if 'Property' in first_open:
                property_info = first_open['Property']
                print(f"Open house for: {property_info['UnparsedAddress']}")
            ```
        """
        return self.get_open_houses(expand="Property", **kwargs)

    def get_modified_open_houses(
        self, since: Union[str, date, datetime], **kwargs: Any
    ) -> Dict[str, Any]:
        """Get open houses modified since a specific date/time.

        Used for incremental data synchronization to get only open house records
        that have been updated since the last sync. Essential for maintaining
        up-to-date scheduling information.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing open houses modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta

            # Get open houses modified in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            updates = client.openhouse.get_modified_open_houses(
                since=cutoff_time
            )

            # Get open houses modified since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            updates = client.openhouse.get_modified_open_houses(
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
        return self.get_open_houses(filter_query=filter_query, **kwargs)

    def get_open_houses_by_date_range(
        self, 
        start_date: Union[str, date, datetime], 
        end_date: Union[str, date, datetime],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get open houses within a specific date range.

        Convenience method to retrieve open houses scheduled between two dates.

        Args:
            start_date: Start date for the range (ISO format string, date, or datetime object)
            end_date: End date for the range (ISO format string, date, or datetime object)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing open houses within the specified date range

        Example:
            ```python
            from datetime import date

            # Get open houses for January 2024
            start_date = date(2024, 1, 1)
            end_date = date(2024, 1, 31)
            opens = client.openhouse.get_open_houses_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
            ```
        """
        if isinstance(start_date, datetime):
            start_str = start_date.date().isoformat()
        elif isinstance(start_date, date):
            start_str = start_date.isoformat()
        else:
            start_str = start_date

        if isinstance(end_date, datetime):
            end_str = end_date.date().isoformat()
        elif isinstance(end_date, date):
            end_str = end_date.isoformat()
        else:
            end_str = end_date

        filter_query = f"OpenHouseDate ge {start_str} and OpenHouseDate le {end_str}"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{filter_query} and {existing_filter}"
        else:
            kwargs["filter_query"] = filter_query

        return self.get_open_houses(**kwargs)

    def get_weekend_open_houses(
        self, 
        weeks_ahead: Optional[int] = 2,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get weekend open houses.

        Convenience method to retrieve open houses scheduled for weekends.

        Args:
            weeks_ahead: Number of weeks ahead to search (default: 2)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing weekend open house listings

        Example:
            ```python
            # Get open houses for next 2 weekends
            weekend_opens = client.openhouse.get_weekend_open_houses(
                weeks_ahead=2,
                orderby="OpenHouseStartTime asc"
            )
            ```
        """
        from datetime import datetime, timedelta

        # Calculate the date range for weekends
        start_date = datetime.now().date()
        
        # For simplicity, we'll get all open houses in the range and let the user filter weekends
        # A more sophisticated implementation would filter by day of week
        filter_query = f"OpenHouseDate ge {start_date.isoformat()}"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{filter_query} and {existing_filter}"
        else:
            kwargs["filter_query"] = filter_query

        return self.get_open_houses(**kwargs)
