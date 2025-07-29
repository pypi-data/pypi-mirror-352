"""PropertyGreenVerification client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class GreenVerificationType(Enum):
    """Green verification type options."""

    ENERGY_STAR = "Energy Star"
    LEED = "LEED"
    GREEN_BUILDING = "Green Building"
    HERS = "HERS"
    OTHER = "Other"


class GreenVerificationClient(BaseClient):
    """Client for property green verification/certification API endpoints.
    
    The PropertyGreenVerification resource contains information about
    environmental certifications and green building verifications for properties.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the green verification client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_green_verifications(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get green verifications with optional OData filtering.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip)
            filter_query: OData filter query string
            select: Fields to select (OData $select)
            orderby: Order by clause (OData $orderby)
            expand: Related resources to include (OData $expand)
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing green verification data

        Example:
            ```python
            # Get LEED certified properties
            leed_properties = client.green.get_green_verifications(
                filter_query="GreenVerificationType eq 'LEED'",
                expand="Property"
            )
            ```
        """
        params: Dict[str, Any] = {}

        if top is not None:
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

        return self.get("PropertyGreenVerification", params=params)

    def get_green_verification(self, verification_key: str) -> Dict[str, Any]:
        """Get green verification by key.

        Args:
            verification_key: Verification key to retrieve

        Returns:
            Dictionary containing verification data
        """
        return self.get(f"PropertyGreenVerification('{verification_key}')")

    def get_verifications_for_property(
        self,
        listing_key: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get green verifications for a specific property.

        Args:
            listing_key: Property listing key
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing verifications for the property
        """
        property_filter = f"ListingKey eq '{listing_key}'"
        
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{property_filter} and {existing_filter}"
        else:
            kwargs['filter_query'] = property_filter
            
        return self.get_green_verifications(**kwargs) 