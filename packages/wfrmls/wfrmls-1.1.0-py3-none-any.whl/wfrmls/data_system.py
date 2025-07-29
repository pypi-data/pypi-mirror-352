"""DataSystem client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class DataSystemClient(BaseClient):
    """Client for data system metadata API endpoints.
    
    The DataSystem resource provides metadata about the data system itself,
    including version information, contact details, and system capabilities.
    This is useful for understanding the MLS system configuration and features.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the data system client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_data_systems(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get data system information with optional OData filtering.

        This method retrieves data system metadata with full OData v4.0 query support.
        Provides information about the MLS system configuration and capabilities.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing data system metadata with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of data system records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get all data system information
            data_systems = client.data_system.get_data_systems()
            
            # Get specific fields only
            data_systems = client.data_system.get_data_systems(
                select=["DataSystemKey", "DataSystemName", "SystemVersion"]
            )

            # Get data systems with specific properties
            data_systems = client.data_system.get_data_systems(
                filter_query="DataSystemName eq 'WFRMLS'",
                expand="Resources"
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

        return self.get("DataSystem", params=params)

    def get_data_system(self, data_system_key: str) -> Dict[str, Any]:
        """Get data system by data system key.

        Retrieves a single data system record by its unique key.
        This is the most efficient way to get detailed information about
        a specific data system configuration.

        Args:
            data_system_key: Data system key to retrieve (unique identifier)

        Returns:
            Dictionary containing data system data for the specified record

        Raises:
            NotFoundError: If the data system with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific data system by key
            data_system = client.data_system.get_data_system("WFRMLS")
            
            print(f"System Name: {data_system['DataSystemName']}")
            print(f"Version: {data_system.get('SystemVersion', 'Unknown')}")
            print(f"Contact: {data_system.get('ContactEmail', 'Unknown')}")
            ```
        """
        return self.get(f"DataSystem('{data_system_key}')")

    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information.

        Convenience method to retrieve basic system information.
        Typically returns information about the primary MLS system.

        Returns:
            Dictionary containing system information

        Example:
            ```python
            # Get system information
            system_info = client.data_system.get_system_info()
            
            for system in system_info.get('value', []):
                print(f"System: {system['DataSystemName']}")
                print(f"Description: {system.get('DataSystemDescription', 'N/A')}")
            ```
        """
        return self.get_data_systems(top=10)

    def get_modified_data_systems(
        self,
        since: Union[str, date, datetime],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get data systems modified since a specific date/time.

        Used for incremental data synchronization to get only data system records
        that have been updated since the last sync. Useful for monitoring
        system configuration changes.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing data systems modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get systems modified in last day
            cutoff_time = datetime.utcnow() - timedelta(days=1)
            updates = client.data_system.get_modified_data_systems(
                since=cutoff_time
            )

            # Get systems modified since a specific date
            updates = client.data_system.get_modified_data_systems(
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
        return self.get_data_systems(filter_query=filter_query, **kwargs) 