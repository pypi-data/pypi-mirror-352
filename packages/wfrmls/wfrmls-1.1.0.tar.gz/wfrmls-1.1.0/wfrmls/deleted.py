"""Deleted records client for WFRMLS API."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class ResourceName(Enum):
    """Resource name options for tracking deletions."""

    PROPERTY = "Property"
    MEMBER = "Member"
    OFFICE = "Office"
    OPENHOUSE = "OpenHouse"
    MEDIA = "Media"
    HISTORY_TRANSACTIONAL = "HistoryTransactional"
    PROPERTY_GREEN_VERIFICATION = "PropertyGreenVerification"
    PROPERTY_UNIT_TYPES = "PropertyUnitTypes"
    ADU = "Adu"


class DeletedClient(BaseClient):
    """Client for deleted records API endpoints.
    
    The Deleted resource tracks records that have been removed from the MLS system.
    This is essential for data synchronization to ensure local databases properly
    handle deletions and maintain data integrity.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the deleted records client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_deleted(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get deleted records with optional OData filtering.

        This method retrieves records that have been deleted from the MLS system.
        Essential for maintaining data synchronization and integrity in applications
        that replicate MLS data.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing deleted record data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of deleted record entries

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get all deleted records
            deleted = client.deleted.get_deleted(top=50)

            # Get deleted Property records only
            deleted_properties = client.deleted.get_deleted(
                filter_query="ResourceName eq 'Property'"
            )

            # Get recent deletions (last 24 hours)
            from datetime import datetime, timedelta
            cutoff = datetime.utcnow() - timedelta(days=1)
            recent_deletions = client.deleted.get_deleted(
                filter_query=f"DeletedDateTime gt {cutoff.isoformat()}Z",
                orderby="DeletedDateTime desc"
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

        return self.get("Deleted", params=params)

    def get_deleted_by_resource(
        self,
        resource_name: Union[ResourceName, str],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get deleted records for a specific resource type.

        Convenience method to filter deleted records by resource type.
        Useful for synchronizing specific types of data.

        Args:
            resource_name: Resource type to filter by (Property, Member, etc.)
            **kwargs: Additional OData parameters (top, orderby, etc.)

        Returns:
            Dictionary containing deleted records for the specified resource

        Example:
            ```python
            # Get deleted properties
            deleted_properties = client.deleted.get_deleted_by_resource(
                resource_name=ResourceName.PROPERTY,
                top=100
            )

            # Get deleted members with ordering
            deleted_members = client.deleted.get_deleted_by_resource(
                resource_name="Member",
                orderby="DeletedDateTime desc"
            )
            ```
        """
        if isinstance(resource_name, ResourceName):
            resource_value = resource_name.value
        else:
            resource_value = resource_name
            
        filter_query = f"ResourceName eq '{resource_value}'"
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{filter_query} and {existing_filter}"
        else:
            kwargs['filter_query'] = filter_query
            
        return self.get_deleted(**kwargs)

    def get_deleted_since(
        self,
        since: Union[str, date],
        resource_name: Optional[Union[ResourceName, str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get records deleted since a specific date/time.

        Used for incremental data synchronization to identify records that have
        been deleted since the last sync. Essential for maintaining data integrity
        in replicated systems.

        Args:
            since: ISO format datetime string or date object for cutoff time
            resource_name: Optional resource type to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing records deleted since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get records deleted in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            recent_deletions = client.deleted.get_deleted_since(
                since=cutoff_time.isoformat() + "Z"
            )

            # Get properties deleted since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            deleted_properties = client.deleted.get_deleted_since(
                since=yesterday.isoformat() + "Z",
                resource_name=ResourceName.PROPERTY
            )
            ```
        """
        if isinstance(since, date):
            since_str = since.isoformat() + "Z"
        else:
            since_str = since
            
        filters = [f"DeletedDateTime gt {since_str}"]
        
        if resource_name is not None:
            if isinstance(resource_name, ResourceName):
                resource_value = resource_name.value
            else:
                resource_value = resource_name
            filters.append(f"ResourceName eq '{resource_value}'")
            
        filter_query = " and ".join(filters)
        
        # If additional filter_query provided, combine them
        existing_filter = kwargs.get('filter_query')
        if existing_filter:
            kwargs['filter_query'] = f"{filter_query} and {existing_filter}"
        else:
            kwargs['filter_query'] = filter_query
            
        return self.get_deleted(**kwargs)

    def get_deleted_property_records(self, **kwargs: Any) -> Dict[str, Any]:
        """Get deleted Property records.

        Convenience method specifically for deleted property records.
        Most commonly used deletion tracking for real estate applications.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing deleted property records

        Example:
            ```python
            # Get recent deleted properties
            deleted_properties = client.deleted.get_deleted_property_records(
                orderby="DeletedDateTime desc",
                top=50
            )
            ```
        """
        return self.get_deleted_by_resource(ResourceName.PROPERTY, **kwargs)

    def get_deleted_member_records(self, **kwargs: Any) -> Dict[str, Any]:
        """Get deleted Member records.

        Convenience method specifically for deleted member (agent/broker) records.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing deleted member records

        Example:
            ```python
            # Get deleted members
            deleted_members = client.deleted.get_deleted_member_records(top=25)
            ```
        """
        return self.get_deleted_by_resource(ResourceName.MEMBER, **kwargs)

    def get_deleted_office_records(self, **kwargs: Any) -> Dict[str, Any]:
        """Get deleted Office records.

        Convenience method specifically for deleted office/brokerage records.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing deleted office records

        Example:
            ```python
            # Get deleted offices
            deleted_offices = client.deleted.get_deleted_office_records(top=25)
            ```
        """
        return self.get_deleted_by_resource(ResourceName.OFFICE, **kwargs)

    def get_deleted_media_records(self, **kwargs: Any) -> Dict[str, Any]:
        """Get deleted Media records.

        Convenience method specifically for deleted media/photo records.
        Useful for cleaning up orphaned media references.

        Args:
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing deleted media records

        Example:
            ```python
            # Get recently deleted media
            deleted_media = client.deleted.get_deleted_media_records(
                orderby="DeletedDateTime desc",
                top=100
            )
            ```
        """
        return self.get_deleted_by_resource(ResourceName.MEDIA, **kwargs)

    def get_all_deleted_for_sync(
        self,
        since: Union[str, date],
        resource_types: Optional[List[Union[ResourceName, str]]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get all deleted records for comprehensive data synchronization.

        Retrieves deleted records across multiple resource types for a complete
        sync operation. Essential for maintaining data integrity in replicated systems.

        Args:
            since: ISO format datetime string or date object for cutoff time
            resource_types: List of resource types to include (all if None)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing comprehensive deleted record data organized by resource type

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get all deletions in last hour for comprehensive sync
            cutoff = datetime.utcnow() - timedelta(hours=1)
            all_deletions = client.deleted.get_all_deleted_for_sync(
                since=cutoff.isoformat() + "Z",
                resource_types=[ResourceName.PROPERTY, ResourceName.MEMBER, ResourceName.MEDIA]
            )
            
            # Process by resource type
            for resource_type in all_deletions['by_resource']:
                records = all_deletions['by_resource'][resource_type]
                print(f"Found {len(records)} deleted {resource_type} records")
            ```
        """
        if isinstance(since, date):
            since_str = since.isoformat() + "Z"
        else:
            since_str = since

        # If no resource types specified, get all major types
        if resource_types is None:
            resource_types = [
                ResourceName.PROPERTY,
                ResourceName.MEMBER,
                ResourceName.OFFICE,
                ResourceName.MEDIA,
                ResourceName.OPENHOUSE
            ]

        all_results = []
        by_resource = {}
        total_count = 0

        for resource_type in resource_types:
            try:
                # Get deleted records for this resource type
                resource_results = self.get_deleted_since(
                    since=since_str,
                    resource_name=resource_type,
                    **kwargs
                )
                
                resource_records = resource_results.get('value', [])
                resource_name = resource_type.value if isinstance(resource_type, ResourceName) else resource_type
                by_resource[resource_name] = resource_records
                all_results.extend(resource_records)
                total_count += len(resource_records)
                
            except Exception:
                # If one resource type fails, continue with others
                resource_name = resource_type.value if isinstance(resource_type, ResourceName) else resource_type
                by_resource[resource_name] = []

        return {
            "@odata.context": "Comprehensive deletion sync",
            "value": all_results,
            "by_resource": by_resource,
            "sync_info": {
                "total_deleted_records": total_count,
                "resource_types_checked": len(resource_types),
                "since_timestamp": since_str,
                "resources_with_deletions": len([r for r in by_resource.values() if r])
            }
        }

    def get_deletion_summary(
        self,
        since: Union[str, date],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Get a summary of deletion activity by resource type.

        Provides overview statistics for deletion monitoring and reporting.
        Useful for understanding deletion patterns and data management needs.

        Args:
            since: ISO format datetime string or date object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing deletion summary statistics

        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Get deletion summary for last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            summary = client.deleted.get_deletion_summary(
                since=yesterday.isoformat() + "Z"
            )
            
            print(f"Total deletions: {summary['summary']['total_deletions']}")
            for resource, count in summary['summary']['by_resource_count'].items():
                print(f"  {resource}: {count} deletions")
            ```
        """
        if isinstance(since, date):
            since_str = since.isoformat() + "Z"
        else:
            since_str = since

        # Get all deleted records since the specified time
        all_deletions = self.get_deleted_since(since=since_str, **kwargs)
        deleted_records = all_deletions.get('value', [])

        # Organize by resource type
        by_resource_count: Dict[str, int] = {}
        by_resource_latest: Dict[str, str] = {}
        
        for record in deleted_records:
            resource_name = record.get('ResourceName', 'Unknown')
            
            # Count by resource type
            if resource_name in by_resource_count:
                by_resource_count[resource_name] += 1
            else:
                by_resource_count[resource_name] = 1
                
            # Track latest deletion time by resource
            deleted_time = record.get('DeletedDateTime')
            if deleted_time:
                if resource_name not in by_resource_latest or deleted_time > by_resource_latest[resource_name]:
                    by_resource_latest[resource_name] = deleted_time

        return {
            "@odata.context": "Deletion summary",
            "value": deleted_records,
            "summary": {
                "total_deletions": len(deleted_records),
                "resource_types_affected": len(by_resource_count),
                "by_resource_count": by_resource_count,
                "by_resource_latest": by_resource_latest,
                "analysis_period": {
                    "since": since_str,
                    "analysis_timestamp": f"{date.today().isoformat()}Z"
                }
            }
        }

    def monitor_deletion_activity(
        self,
        hours_back: int = 24,
        alert_threshold: int = 100,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Monitor deletion activity and identify unusual patterns.

        Analyzes recent deletion activity to identify potential issues or
        unusual deletion patterns that might require attention.

        Args:
            hours_back: Number of hours to analyze (default: 24)
            alert_threshold: Number of deletions that triggers alerts (default: 100)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing monitoring results and alerts

        Example:
            ```python
            # Monitor for unusual deletion activity
            monitoring = client.deleted.monitor_deletion_activity(
                hours_back=6,
                alert_threshold=50
            )
            
            if monitoring['alerts']:
                print("ALERTS DETECTED:")
                for alert in monitoring['alerts']:
                    print(f"  - {alert}")
            ```
        """
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        since_str = cutoff_time.isoformat() + "Z"

        # Get deletion summary for the period
        summary = self.get_deletion_summary(since=since_str, **kwargs)
        
        alerts = []
        recommendations = []
        
        total_deletions = summary['summary']['total_deletions']
        by_resource_count = summary['summary']['by_resource_count']
        
        # Check for high deletion volumes
        if total_deletions > alert_threshold:
            alerts.append(f"High deletion volume: {total_deletions} records deleted in {hours_back} hours")
        
        # Check for resource-specific alerts
        for resource_type, count in by_resource_count.items():
            resource_threshold = alert_threshold // len(by_resource_count) if by_resource_count else alert_threshold
            if count > resource_threshold:
                alerts.append(f"High {resource_type} deletions: {count} records")
                
        # Generate recommendations
        if total_deletions > 0:
            recommendations.append("Consider running data integrity checks after bulk deletions")
            
        if 'Property' in by_resource_count and by_resource_count['Property'] > 10:
            recommendations.append("Review property deletion patterns for market analysis")
            
        if 'Media' in by_resource_count and by_resource_count['Media'] > 50:
            recommendations.append("Check for orphaned media cleanup processes")

        return {
            "@odata.context": "Deletion monitoring",
            "monitoring_period": f"{hours_back} hours",
            "summary": summary['summary'],
            "alerts": alerts,
            "recommendations": recommendations,
            "status": "ALERT" if alerts else "NORMAL",
            "monitoring_timestamp": datetime.utcnow().isoformat() + "Z"
        } 