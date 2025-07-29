"""Main WFRMLS client."""

from builtins import property as property_decorator
from typing import TYPE_CHECKING, Any, Dict, Optional

from .exceptions import WFRMLSError

# Use TYPE_CHECKING to avoid import cycles and property conflicts
if TYPE_CHECKING:
    from .adu import AduClient
    from .data_system import DataSystemClient
    from .deleted import DeletedClient
    from .lookup import LookupClient
    from .member import MemberClient
    from .office import OfficeClient
    from .openhouse import OpenHouseClient
    from .properties import PropertyClient
    from .property_unit_types import PropertyUnitTypesClient
    from .resource import ResourceClient


class WFRMLSClient:
    """Main client for WFRMLS API.

    This is the primary entry point for accessing the WFRMLS API. It provides
    access to all available resources through service-specific client properties.
    The client uses lazy initialization to create service clients only when accessed.

    Note: Media, History, and Green Verification endpoints are currently unavailable
    due to server-side issues (504 Gateway Timeouts and missing entity types).

    Example:
        ```python
        from wfrmls import WFRMLSClient

        # Initialize with bearer token from environment variable
        client = WFRMLSClient()

        # Or provide bearer token directly
        client = WFRMLSClient(bearer_token="your_bearer_token_here")

        # Discover available resources
        service_doc = client.get_service_document()
        metadata = client.get_metadata()

        # Use service endpoints
        properties = client.property.get_properties(top=10)
        property_detail = client.property.get_property("12345678")

        # Search properties by location
        properties = client.property.search_properties_by_radius(
            latitude=40.7608, longitude=-111.8910, radius_miles=10
        )

        # Get open houses
        open_houses = client.openhouse.get_upcoming_open_houses(days_ahead=7)

        # Get member information
        members = client.member.get_active_members(top=50)

        # Get office information
        offices = client.office.get_active_offices(top=50)
        ```
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the client.

        Args:
            bearer_token: Bearer token for authentication. If not provided,
                will attempt to load from WFRMLS_BEARER_TOKEN environment variable.
            base_url: Base URL for the API. Defaults to the production WFRMLS API.

        Raises:
            AuthenticationError: If no bearer token is provided or found in environment.
        """
        self._bearer_token = bearer_token
        self._base_url = base_url

        # Service clients - lazily initialized
        self._property: Optional["PropertyClient"] = None
        self._member: Optional["MemberClient"] = None
        self._office: Optional["OfficeClient"] = None
        self._openhouse: Optional["OpenHouseClient"] = None
        self._data_system: Optional["DataSystemClient"] = None
        self._resource: Optional["ResourceClient"] = None
        self._property_unit_types: Optional["PropertyUnitTypesClient"] = None
        self._lookup: Optional["LookupClient"] = None
        self._adu: Optional["AduClient"] = None
        self._deleted: Optional["DeletedClient"] = None

        # Base client for service discovery - lazily initialized
        self._base_client: Optional[Any] = None

    def _get_base_client(self) -> Any:
        """Get base client instance for service discovery."""
        if self._base_client is None:
            from .base_client import BaseClient

            self._base_client = BaseClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._base_client

    def get_service_document(self) -> Dict[str, Any]:
        """Get the OData service document.

        The service document provides a list of all available resources (entity sets)
        that can be accessed through the API. This is essential for discovering
        what endpoints are available for the authenticated user.

        Returns:
            Dictionary containing the service document with available resources

        Raises:
            WFRMLSError: If the API request fails
            AuthenticationError: If authentication fails

        Example:
            ```python
            # Get available resources
            service_doc = client.get_service_document()

            # List available entity sets
            for resource in service_doc.get('value', []):
                print(f"Resource: {resource['name']} - {resource['url']}")
            ```
        """
        from typing import cast

        base_client = self._get_base_client()
        result = base_client.get("")  # Root endpoint returns service document
        return cast(Dict[str, Any], result)

    def get_metadata(self) -> str:
        """Get the OData metadata document.

        The metadata document provides the complete schema definition including
        entity types, properties, relationships, and enumerations. This is
        essential for understanding the structure of the data model.

        Returns:
            XML string containing the complete metadata schema

        Raises:
            WFRMLSError: If the API request fails
            AuthenticationError: If authentication fails

        Example:
            ```python
            # Get metadata schema
            metadata_xml = client.get_metadata()

            # Save to file for inspection
            with open('wfrmls_metadata.xml', 'w') as f:
                f.write(metadata_xml)
            ```
        """
        base_client = self._get_base_client()
        # For metadata, we need to handle the raw response since it's XML
        import requests

        url = f"{base_client.base_url}/$metadata"
        headers = {
            "Authorization": f"Bearer {base_client.bearer_token}",
            "Accept": "application/xml",
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise WFRMLSError(f"Failed to fetch metadata: {response.status_code}")

        return response.text

    @property_decorator
    def property(self) -> "PropertyClient":
        """Access to property endpoints.

        Provides access to property listings, search functionality, and property details.
        This is the primary resource for real estate data in the WFRMLS system.

        Returns:
            PropertyClient instance for property operations

        Example:
            ```python
            # Get active properties
            properties = client.property.get_active_properties(top=50)

            # Get property with photos
            property_with_media = client.property.get_properties_with_media(
                filter_query="ListingId eq '12345678'"
            )
            ```
        """
        if self._property is None:
            from .properties import PropertyClient

            self._property = PropertyClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._property

    @property_decorator
    def member(self) -> "MemberClient":
        """Access to member (agent/broker) endpoints.

        Provides access to real estate agent and broker information,
        including contact details, office affiliations, and licensing data.

        Returns:
            MemberClient instance for member operations

        Example:
            ```python
            # Get active members
            members = client.member.get_active_members(top=50)

            # Get member with office info
            member_with_office = client.member.get_members_with_office(
                filter_query="MemberKey eq '12345'"
            )
            ```
        """
        if self._member is None:
            from .member import MemberClient

            self._member = MemberClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._member

    @property_decorator
    def office(self) -> "OfficeClient":
        """Access to office (brokerage) endpoints.

        Provides access to real estate office and brokerage information,
        including contact details, addresses, and licensing information.

        Returns:
            OfficeClient instance for office operations

        Example:
            ```python
            # Get active offices
            offices = client.office.get_active_offices(top=50)

            # Get office with members
            office_with_members = client.office.get_offices_with_members(
                filter_query="OfficeKey eq '12345'"
            )
            ```
        """
        if self._office is None:
            from .office import OfficeClient

            self._office = OfficeClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._office

    @property_decorator
    def openhouse(self) -> "OpenHouseClient":
        """Access to open house schedule endpoints.

        Provides access to open house schedules, events, and showing information.
        Useful for finding upcoming open houses and managing showing schedules.

        Returns:
            OpenHouseClient instance for open house operations

        Example:
            ```python
            # Get upcoming open houses
            open_houses = client.openhouse.get_upcoming_open_houses(days_ahead=7)

            # Get open houses for a property
            property_opens = client.openhouse.get_open_houses_for_property("1611952")

            # Get open houses by agent
            agent_opens = client.openhouse.get_open_houses_by_agent("96422")
            ```
        """
        if self._openhouse is None:
            from .openhouse import OpenHouseClient

            self._openhouse = OpenHouseClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._openhouse

    @property_decorator
    def data_system(self) -> "DataSystemClient":
        """Access to data system metadata endpoints.

        Provides access to data system information, including version details,
        contact information, and system capabilities.

        Returns:
            DataSystemClient instance for data system operations

        Example:
            ```python
            # Get system information
            system_info = client.data_system.get_system_info()

            # Get specific data system by key
            system = client.data_system.get_data_system("WFRMLS")
            ```
        """
        if self._data_system is None:
            from .data_system import DataSystemClient

            self._data_system = DataSystemClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._data_system

    @property_decorator
    def resource(self) -> "ResourceClient":
        """Access to resource metadata endpoints.

        Provides access to API resource metadata, including field definitions,
        data types, and resource relationships.

        Returns:
            ResourceClient instance for resource metadata operations

        Example:
            ```python
            # Get all resources
            resources = client.resource.get_resources()

            # Get Property resource metadata
            property_resource = client.resource.get_resource_by_name("Property")
            ```
        """
        if self._resource is None:
            from .resource import ResourceClient

            self._resource = ResourceClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._resource

    @property_decorator
    def property_unit_types(self) -> "PropertyUnitTypesClient":
        """Access to property unit types endpoints.

        Provides access to property unit type information, including condos,
        townhomes, apartments, and other unit classifications.

        Returns:
            PropertyUnitTypesClient instance for unit type operations

        Example:
            ```python
            # Get all unit types
            unit_types = client.property_unit_types.get_property_unit_types()

            # Get residential unit types
            residential = client.property_unit_types.get_residential_unit_types()
            ```
        """
        if self._property_unit_types is None:
            from .property_unit_types import PropertyUnitTypesClient

            self._property_unit_types = PropertyUnitTypesClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._property_unit_types

    @property_decorator
    def lookup(self) -> "LookupClient":
        """Access to lookup table endpoints.

        Provides access to enumeration values and reference data used throughout
        the MLS system, including property types, statuses, and other lookup values.

        Returns:
            LookupClient instance for lookup operations

        Example:
            ```python
            # Get property type lookups
            property_types = client.lookup.get_property_type_lookups()

            # Get all lookup names
            lookup_names = client.lookup.get_lookup_names()
            ```
        """
        if self._lookup is None:
            from .lookup import LookupClient

            self._lookup = LookupClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._lookup

    @property_decorator
    def adu(self) -> "AduClient":
        """Access to Accessory Dwelling Unit (ADU) endpoints.

        Provides access to accessory dwelling unit information, including
        types, statuses, and property relationships for secondary housing units.

        Returns:
            AduClient instance for ADU operations

        Example:
            ```python
            # Get all ADUs
            adus = client.adu.get_adus()

            # Get existing ADUs
            existing_adus = client.adu.get_existing_adus()

            # Get ADUs for a property
            property_adus = client.adu.get_adus_for_property("1611952")
            ```
        """
        if self._adu is None:
            from .adu import AduClient

            self._adu = AduClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._adu

    @property_decorator
    def deleted(self) -> "DeletedClient":
        """Access to deleted records endpoints.

        Provides access to deleted record tracking for data synchronization.
        Essential for maintaining data integrity when replicating MLS data.

        Returns:
            DeletedClient instance for deleted record operations

        Example:
            ```python
            # Get all deleted records
            deleted = client.deleted.get_deleted(top=50)

            # Get deleted properties since yesterday
            from datetime import datetime, timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            deleted_properties = client.deleted.get_deleted_since(
                since=yesterday.isoformat() + "Z",
                resource_name="Property"
            )

            # Get recent deletions for synchronization
            recent_deletions = client.deleted.get_deleted_property_records(
                orderby="DeletedDateTime desc"
            )
            ```
        """
        if self._deleted is None:
            from .deleted import DeletedClient

            self._deleted = DeletedClient(
                bearer_token=self._bearer_token, base_url=self._base_url
            )
        return self._deleted
