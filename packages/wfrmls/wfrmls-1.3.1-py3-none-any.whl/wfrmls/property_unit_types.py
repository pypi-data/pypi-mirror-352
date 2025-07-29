"""PropertyUnitTypes client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class PropertyUnitTypesClient(BaseClient):
    """Client for property unit types API endpoints.

    The PropertyUnitTypes resource contains information about different types
    of property units such as condos, townhomes, apartments, etc. This is useful
    for understanding property classification and unit-specific details.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the property unit types client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_property_unit_types(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get property unit types with optional OData filtering.

        This method retrieves property unit type information with full OData v4.0 query support.
        Provides information about different unit types and their characteristics.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing property unit type data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of property unit type records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get all unit types
            unit_types = client.property_unit_types.get_property_unit_types()

            # Get specific unit types
            unit_types = client.property_unit_types.get_property_unit_types(
                filter_query="UnitType eq 'Condo'",
                select=["UnitTypeKey", "UnitType", "Description"]
            )

            # Get unit types with property relationships
            unit_types = client.property_unit_types.get_property_unit_types(
                expand="Properties",
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

        return self.get("PropertyUnitTypes", params=params)

    def get_property_unit_type(self, unit_type_key: str) -> Dict[str, Any]:
        """Get property unit type by unit type key.

        Retrieves a single property unit type record by its unique key.
        This is the most efficient way to get detailed information about
        a specific unit type.

        Args:
            unit_type_key: Unit type key to retrieve (unique identifier)

        Returns:
            Dictionary containing unit type data for the specified record

        Raises:
            NotFoundError: If the unit type with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific unit type by key
            unit_type = client.property_unit_types.get_property_unit_type("CONDO")

            print(f"Unit Type: {unit_type['UnitType']}")
            print(f"Description: {unit_type.get('Description', 'No description')}")
            ```
        """
        return self.get(f"PropertyUnitTypes('{unit_type_key}')")

    def get_unit_types_for_property(
        self, listing_key: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get unit types for a specific property.

        Convenience method to retrieve unit type information for a property.
        Useful for understanding what types of units a property contains.

        Args:
            listing_key: Property listing key to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing unit types for the specified property

        Example:
            ```python
            # Get unit types for a property
            property_units = client.property_unit_types.get_unit_types_for_property(
                listing_key="1611952"
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

        return self.get_property_unit_types(**kwargs)

    def get_unit_types_by_type(self, unit_type: str, **kwargs: Any) -> Dict[str, Any]:
        """Get properties by unit type.

        Convenience method to filter unit types by type name.
        Useful for finding all instances of a specific unit type.

        Args:
            unit_type: Unit type to filter by (e.g., "Condo", "Townhome")
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing unit types matching the specified type

        Example:
            ```python
            # Get all condo unit types
            condos = client.property_unit_types.get_unit_types_by_type(
                unit_type="Condo",
                expand="Properties"
            )

            # Get all townhome unit types
            townhomes = client.property_unit_types.get_unit_types_by_type("Townhome")
            ```
        """
        type_filter = f"UnitType eq '{unit_type}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{type_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = type_filter

        return self.get_property_unit_types(**kwargs)

    def get_residential_unit_types(self, **kwargs: Any) -> Dict[str, Any]:
        """Get residential unit types.

        Convenience method to filter for common residential unit types.
        Excludes commercial and other non-residential unit types.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing residential unit types

        Example:
            ```python
            # Get all residential unit types
            residential_units = client.property_unit_types.get_residential_unit_types()

            for unit in residential_units.get('value', []):
                print(f"Residential Unit: {unit['UnitType']}")
            ```
        """
        # Common residential unit type filters
        residential_types = [
            "UnitType eq 'Condo'",
            "UnitType eq 'Townhome'",
            "UnitType eq 'Apartment'",
            "UnitType eq 'Single Family'",
            "UnitType eq 'Duplex'",
            "UnitType eq 'Triplex'",
            "UnitType eq 'Fourplex'",
        ]

        residential_filter = " or ".join(residential_types)
        residential_filter = f"({residential_filter})"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{residential_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = residential_filter

        return self.get_property_unit_types(**kwargs)

    def get_unit_types_with_properties(self, **kwargs: Any) -> Dict[str, Any]:
        """Get unit types with their property information expanded.

        This is a convenience method that automatically expands property
        relationships to include property details in the response.
        More efficient than making separate requests for unit types and properties.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing unit type data with expanded property relationships

        Example:
            ```python
            # Get unit types with property information
            units_with_props = client.property_unit_types.get_unit_types_with_properties(
                top=10
            )

            # Access property info for first unit type
            first_unit = units_with_props['value'][0]
            if 'Properties' in first_unit:
                properties = first_unit['Properties']
                print(f"Unit type {first_unit['UnitType']} has {len(properties)} properties")
            ```
        """
        return self.get_property_unit_types(expand="Properties", **kwargs)

    def get_modified_unit_types(
        self, since: Union[str, date, datetime], **kwargs: Any
    ) -> Dict[str, Any]:
        """Get unit types modified since a specific date/time.

        Used for incremental data synchronization to get only unit type records
        that have been updated since the last sync. Useful for maintaining
        up-to-date unit type information.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing unit types modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta

            # Get unit types modified in last week
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            updates = client.property_unit_types.get_modified_unit_types(
                since=cutoff_time
            )

            # Get unit types modified since a specific date
            updates = client.property_unit_types.get_modified_unit_types(
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
        return self.get_property_unit_types(filter_query=filter_query, **kwargs)
