"""Resource client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class ResourceClient(BaseClient):
    """Client for resource metadata API endpoints.

    The Resource endpoint provides metadata about API resources, including
    field definitions, data types, and relationships. This is essential for
    understanding the structure and capabilities of each resource.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the resource client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_resources(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get resource metadata with optional OData filtering.

        This method retrieves resource metadata with full OData v4.0 query support.
        Provides detailed information about API resources, fields, and capabilities.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing resource metadata with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of resource records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get all resource metadata
            resources = client.resource.get_resources()

            # Get specific resource information
            resources = client.resource.get_resources(
                filter_query="ResourceName eq 'Property'",
                select=["ResourceName", "StandardName", "Description"]
            )

            # Get resources with field information
            resources = client.resource.get_resources(
                expand="Fields",
                top=10
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

        return self.get("Resource", params=params)

    def get_resource(self, resource_key: str) -> Dict[str, Any]:
        """Get resource by resource key.

        Retrieves a single resource record by its unique key.
        This is the most efficient way to get detailed information about
        a specific API resource and its metadata.

        Args:
            resource_key: Resource key to retrieve (unique identifier)

        Returns:
            Dictionary containing resource data for the specified record

        Raises:
            NotFoundError: If the resource with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific resource by key
            resource = client.resource.get_resource("Property")

            print(f"Resource Name: {resource['ResourceName']}")
            print(f"Standard Name: {resource.get('StandardName', 'Unknown')}")
            print(f"Description: {resource.get('Description', 'No description')}")
            ```
        """
        return self.get(f"Resource('{resource_key}')")

    def get_resource_by_name(self, resource_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Get resource by resource name.

        Convenience method to filter resources by name.
        Useful for finding information about a specific resource type.

        Args:
            resource_name: Resource name to filter by (e.g., "Property", "Member")
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing resources matching the specified name

        Example:
            ```python
            # Get Property resource information
            property_resource = client.resource.get_resource_by_name(
                resource_name="Property",
                expand="Fields"
            )

            # Get Member resource information
            member_resource = client.resource.get_resource_by_name("Member")
            ```
        """
        resource_filter = f"ResourceName eq '{resource_name}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{resource_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = resource_filter

        return self.get_resources(**kwargs)

    def get_standard_resources(self, **kwargs: Any) -> Dict[str, Any]:
        """Get standard RESO resources.

        Convenience method to filter for standard RESO-defined resources.
        These are the core resources defined by the RESO standard.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing standard RESO resources

        Example:
            ```python
            # Get all standard resources
            standard_resources = client.resource.get_standard_resources()

            for resource in standard_resources.get('value', []):
                print(f"Standard Resource: {resource['StandardName']}")
            ```
        """
        # Filter for resources that have a StandardName (RESO standard resources)
        standard_filter = "StandardName ne null"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{standard_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = standard_filter

        return self.get_resources(**kwargs)

    def get_resources_with_fields(self, **kwargs: Any) -> Dict[str, Any]:
        """Get resources with their field information expanded.

        This is a convenience method that automatically expands field
        relationships to include detailed field metadata in the response.
        More efficient than making separate requests for resources and fields.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing resource data with expanded field relationships

        Example:
            ```python
            # Get all resources with field information
            resources_with_fields = client.resource.get_resources_with_fields(top=10)

            # Access field info for first resource
            first_resource = resources_with_fields['value'][0]
            if 'Fields' in first_resource:
                fields = first_resource['Fields']
                print(f"Resource {first_resource['ResourceName']} has {len(fields)} fields")
            ```
        """
        return self.get_resources(expand="Fields", **kwargs)

    def get_modified_resources(
        self, since: Union[str, date, datetime], **kwargs: Any
    ) -> Dict[str, Any]:
        """Get resources modified since a specific date/time.

        Used for incremental data synchronization to get only resource records
        that have been updated since the last sync. Useful for monitoring
        schema changes and updates to resource definitions.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing resources modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta

            # Get resources modified in last month
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            updates = client.resource.get_modified_resources(
                since=cutoff_time
            )

            # Get resources modified since a specific date
            updates = client.resource.get_modified_resources(
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
        return self.get_resources(filter_query=filter_query, **kwargs)
