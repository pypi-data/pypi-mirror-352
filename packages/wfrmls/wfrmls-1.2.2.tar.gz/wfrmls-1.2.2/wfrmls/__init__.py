"""WFRMLS Python Client.

A comprehensive Python wrapper for the Wasatch Front Regional MLS (WFRMLS) API,
providing easy access to all RESO-certified endpoints.

Example:
    ```python
    from wfrmls import WFRMLSClient

    # Initialize client
    client = WFRMLSClient(bearer_token="your_token")

    # Get properties
    properties = client.property.get_properties(top=10)

    # Get open houses
    open_houses = client.openhouse.get_upcoming_open_houses(days_ahead=7)

    # Get property photos
    photos = client.media.get_photos_for_property("1611952")

    # Get transaction history
    sales = client.history.get_recent_sales(days_back=30)
    ```
"""

from .adu import AduClient, AduStatus, AduType
from .analytics import WFRMLSAnalytics
from .client import WFRMLSClient
from .data_system import DataSystemClient
from .deleted import DeletedClient, ResourceName
from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    WFRMLSError,
)
from .green_verification import GreenVerificationClient, GreenVerificationType
from .history import HistoryStatus, HistoryTransactionalClient, HistoryTransactionType
from .lookup import LookupClient
from .media import MediaCategory, MediaClient, MediaType
from .member import MemberClient, MemberStatus, MemberType
from .office import OfficeClient, OfficeStatus, OfficeType
from .openhouse import (
    OpenHouseAttendedBy,
    OpenHouseClient,
    OpenHouseStatus,
    OpenHouseType,
)
from .properties import PropertyClient, PropertyStatus, PropertyType
from .property_unit_types import PropertyUnitTypesClient
from .resource import ResourceClient

__version__ = "1.2.2"
__all__ = [
    "WFRMLSClient",
    "PropertyClient",
    "PropertyStatus",
    "PropertyType",
    "MemberClient",
    "MemberStatus",
    "MemberType",
    "OfficeClient",
    "OfficeStatus",
    "OfficeType",
    "OpenHouseClient",
    "OpenHouseStatus",
    "OpenHouseType",
    "OpenHouseAttendedBy",
    "MediaClient",
    "MediaType",
    "MediaCategory",
    "HistoryTransactionalClient",
    "HistoryTransactionType",
    "HistoryStatus",
    "GreenVerificationClient",
    "GreenVerificationType",
    "WFRMLSError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "DataSystemClient",
    "ResourceClient",
    "PropertyUnitTypesClient",
    "LookupClient",
    "AduClient",
    "AduType",
    "AduStatus",
    "DeletedClient",
    "ResourceName",
    "WFRMLSAnalytics",
]
