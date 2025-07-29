"""Tests for deleted records client."""

from datetime import date, datetime, timedelta
from typing import Any, Dict

import pytest
import responses

from wfrmls.deleted import DeletedClient, ResourceName
from wfrmls.exceptions import NotFoundError, ValidationError, WFRMLSError


class TestDeletedClientInit:
    """Test DeletedClient initialization."""

    def test_init_with_bearer_token(self) -> None:
        """Test initialization with provided bearer token."""
        client = DeletedClient(bearer_token="test_token")
        assert client.bearer_token == "test_token"

    def test_init_with_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = DeletedClient(
            bearer_token="test_token", base_url="https://custom.api.com"
        )
        assert client.base_url == "https://custom.api.com"


class TestDeletedClient:
    """Test DeletedClient methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = DeletedClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_deleted_success(self) -> None:
        """Test successful get deleted records request."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata#Deleted",
            "value": [
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": "12345678",
                    "DeletedDateTime": "2024-01-15T10:30:00Z",
                },
                {
                    "ResourceName": "Member",
                    "ResourceRecordKey": "87654321",
                    "DeletedDateTime": "2024-01-15T11:00:00Z",
                },
            ],
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_deleted_with_odata_params(self) -> None:
        """Test get deleted records with OData parameters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(
            top=10,
            skip=20,
            filter_query="ResourceName eq 'Property'",
            select=["ResourceName", "ResourceRecordKey", "DeletedDateTime"],
            orderby="DeletedDateTime desc",
            count=True,
        )

        assert result == mock_response

        # Verify query parameters (URL encoded)
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "%24skip=20" in request.url
        assert "%24filter=ResourceName+eq+%27Property%27" in request.url
        assert "ResourceName" in request.url
        assert "ResourceRecordKey" in request.url
        assert "DeletedDateTime" in request.url
        assert "%24orderby=DeletedDateTime+desc" in request.url
        assert "%24count=true" in request.url

    @responses.activate
    def test_get_deleted_with_expand_list(self) -> None:
        """Test get deleted records with expand parameter as list."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(expand=["ResourceDetails", "AuditInfo"])

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ResourceDetails" in request.url
        assert "AuditInfo" in request.url

    @responses.activate
    def test_get_deleted_with_expand_string(self) -> None:
        """Test get deleted records with expand parameter as string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(expand="ResourceDetails")

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "ResourceDetails" in request.url

    @responses.activate
    def test_get_deleted_count_false(self) -> None:
        """Test get deleted records with count=False."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(count=False)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24count=false" in request.url

    @responses.activate
    def test_get_deleted_by_resource_with_enum(self) -> None:
        """Test get deleted records by resource using enum."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name=ResourceName.PROPERTY, top=50
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=50" in request.url
        assert "%24filter=ResourceName+eq+%27Property%27" in request.url

    @responses.activate
    def test_get_deleted_by_resource_with_string(self) -> None:
        """Test get deleted records by resource using string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name="Member", orderby="DeletedDateTime desc"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert (
            "ResourceName+eq+%27Member%27" in request.url
            or "ResourceName eq 'Member'" in request.url
        )
        assert (
            "DeletedDateTime+desc" in request.url
            or "DeletedDateTime desc" in request.url
        )

    @responses.activate
    def test_get_deleted_by_resource_combined_filters(self) -> None:
        """Test get deleted by resource with existing filter query."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name=ResourceName.PROPERTY,
            filter_query="DeletedDateTime gt 2024-01-01T00:00:00Z",
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        # Should contain both filters combined with 'and'
        assert "ResourceName" in request.url
        assert "Property" in request.url
        assert "DeletedDateTime" in request.url

    @responses.activate
    def test_get_deleted_since_with_datetime_string(self) -> None:
        """Test get deleted records since a datetime string."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deleted_since(since=cutoff_time, top=25)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=25" in request.url
        assert "DeletedDateTime+gt" in request.url

    @responses.activate
    def test_get_deleted_since_with_date_object(self) -> None:
        """Test get deleted records since a date object."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_date = date(2024, 1, 15)
        result = self.client.get_deleted_since(since=cutoff_date)

        assert result == mock_response
        request = responses.calls[0].request
        assert request.url is not None
        assert "DeletedDateTime+gt" in request.url
        assert "2024-01-15" in request.url

    @responses.activate
    def test_get_deleted_since_with_resource_filter(self) -> None:
        """Test get deleted records since a time with resource filter."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deleted_since(
            since=cutoff_time, resource_name=ResourceName.PROPERTY
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "DeletedDateTime+gt" in request.url
        assert (
            "ResourceName+eq+%27Property%27" in request.url
            or "ResourceName eq 'Property'" in request.url
        )

    @responses.activate
    def test_get_deleted_since_with_string_resource_name(self) -> None:
        """Test get deleted since with string resource name."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deleted_since(
            since=cutoff_time, resource_name="Member"
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "DeletedDateTime+gt" in request.url
        assert (
            "ResourceName+eq+%27Member%27" in request.url
            or "ResourceName eq 'Member'" in request.url
        )

    @responses.activate
    def test_get_deleted_since_with_existing_filter(self) -> None:
        """Test get deleted since with existing filter query."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deleted_since(
            since=cutoff_time,
            resource_name=ResourceName.PROPERTY,
            filter_query="ResourceRecordKey ne null",
        )

        assert result == mock_response
        request = responses.calls[0].request
        # Should contain all filters combined
        assert "DeletedDateTime+gt" in request.url
        assert "ResourceName" in request.url
        assert "Property" in request.url

    @responses.activate
    def test_get_deleted_property_records(self) -> None:
        """Test get deleted property records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_property_records(top=30)

        assert result == mock_response
        request = responses.calls[0].request
        assert "%24top=30" in request.url
        assert (
            "ResourceName+eq+%27Property%27" in request.url
            or "ResourceName eq 'Property'" in request.url
        )

    @responses.activate
    def test_get_deleted_member_records(self) -> None:
        """Test get deleted member records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_member_records(orderby="DeletedDateTime desc")

        assert result == mock_response
        request = responses.calls[0].request
        assert (
            "ResourceName+eq+%27Member%27" in request.url
            or "ResourceName eq 'Member'" in request.url
        )
        assert (
            "DeletedDateTime+desc" in request.url
            or "DeletedDateTime desc" in request.url
        )

    @responses.activate
    def test_get_deleted_office_records(self) -> None:
        """Test get deleted office records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_office_records(top=10)

        assert result == mock_response
        request = responses.calls[0].request
        assert "%24top=10" in request.url
        assert (
            "ResourceName+eq+%27Office%27" in request.url
            or "ResourceName eq 'Office'" in request.url
        )

    @responses.activate
    def test_get_deleted_media_records(self) -> None:
        """Test get deleted media records convenience method."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_media_records(top=100)

        assert result == mock_response
        request = responses.calls[0].request
        assert "%24top=100" in request.url
        assert (
            "ResourceName+eq+%27Media%27" in request.url
            or "ResourceName eq 'Media'" in request.url
        )

    @responses.activate
    def test_get_all_deleted_for_sync_success(self) -> None:
        """Test get all deleted for sync with successful responses."""
        # Mock responses for each resource type
        property_response = {
            "value": [{"ResourceName": "Property", "ResourceRecordKey": "P1"}]
        }
        member_response = {
            "value": [{"ResourceName": "Member", "ResourceRecordKey": "M1"}]
        }
        office_response = {
            "value": [{"ResourceName": "Office", "ResourceRecordKey": "O1"}]
        }
        media_response = {
            "value": [{"ResourceName": "Media", "ResourceRecordKey": "MD1"}]
        }
        openhouse_response = {
            "value": [{"ResourceName": "OpenHouse", "ResourceRecordKey": "OH1"}]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=property_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=member_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=office_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=media_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=openhouse_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_all_deleted_for_sync(since=cutoff_time)

        assert "@odata.context" in result
        assert result["@odata.context"] == "Comprehensive deletion sync"
        assert "value" in result
        assert "by_resource" in result
        assert "sync_info" in result

        # Should have 5 records total (one from each resource type)
        assert len(result["value"]) == 5
        assert result["sync_info"]["total_deleted_records"] == 5
        assert result["sync_info"]["since_timestamp"] == cutoff_time

    @responses.activate
    def test_get_all_deleted_for_sync_with_custom_resource_types(self) -> None:
        """Test get all deleted for sync with custom resource types."""
        property_response = {
            "value": [{"ResourceName": "Property", "ResourceRecordKey": "P1"}]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=property_response,
            status=200,
        )

        cutoff_time = date(2024, 1, 15)
        result = self.client.get_all_deleted_for_sync(
            since=cutoff_time, resource_types=[ResourceName.PROPERTY]
        )

        assert result["sync_info"]["total_deleted_records"] == 1
        assert "Property" in result["by_resource"]
        assert len(result["value"]) == 1

    @responses.activate
    def test_get_all_deleted_for_sync_with_exceptions(self) -> None:
        """Test get all deleted for sync handles exceptions gracefully."""
        # First call succeeds, second fails
        property_response = {
            "value": [{"ResourceName": "Property", "ResourceRecordKey": "P1"}]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=property_response,
            status=200,
        )
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            status=500,  # This will cause an exception
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_all_deleted_for_sync(
            since=cutoff_time,
            resource_types=[ResourceName.PROPERTY, ResourceName.MEMBER],
        )

        # Should still return results for successful calls
        assert result["sync_info"]["total_deleted_records"] == 1
        assert "Property" in result["by_resource"]
        assert "Member" in result["by_resource"]
        assert result["by_resource"]["Member"] == []  # Empty due to exception

    @responses.activate
    def test_get_deletion_summary_success(self) -> None:
        """Test get deletion summary with successful response."""
        mock_response = {
            "value": [
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": "P1",
                    "DeletedDateTime": "2024-01-15T10:30:00Z",
                },
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": "P2",
                    "DeletedDateTime": "2024-01-15T11:00:00Z",
                },
                {
                    "ResourceName": "Member",
                    "ResourceRecordKey": "M1",
                    "DeletedDateTime": "2024-01-15T10:45:00Z",
                },
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deletion_summary(since=cutoff_time)

        assert "@odata.context" in result
        assert result["@odata.context"] == "Deletion summary"
        assert "value" in result
        assert "summary" in result

        summary = result["summary"]
        assert summary["total_deletions"] == 3
        assert summary["resource_types_affected"] == 2
        assert summary["by_resource_count"]["Property"] == 2
        assert summary["by_resource_count"]["Member"] == 1
        assert summary["by_resource_latest"]["Property"] == "2024-01-15T11:00:00Z"
        assert summary["by_resource_latest"]["Member"] == "2024-01-15T10:45:00Z"

    @responses.activate
    def test_get_deletion_summary_with_date_object(self) -> None:
        """Test get deletion summary with date object."""
        mock_response: Dict[str, Any] = {"value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_date = date(2024, 1, 15)
        result = self.client.get_deletion_summary(since=cutoff_date)

        assert result["summary"]["total_deletions"] == 0
        assert result["summary"]["analysis_period"]["since"] == "2024-01-15Z"

    @responses.activate
    def test_get_deletion_summary_missing_fields(self) -> None:
        """Test get deletion summary with records missing fields."""
        mock_response = {
            "value": [
                {"ResourceRecordKey": "P1"},  # Missing ResourceName and DeletedDateTime
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": "P2",
                },  # Missing DeletedDateTime
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        cutoff_time = "2024-01-15T10:00:00Z"
        result = self.client.get_deletion_summary(since=cutoff_time)

        summary = result["summary"]
        assert summary["total_deletions"] == 2
        assert "Unknown" in summary["by_resource_count"]
        assert "Property" in summary["by_resource_count"]

    @responses.activate
    def test_monitor_deletion_activity_normal(self) -> None:
        """Test monitor deletion activity under normal conditions."""
        mock_response = {
            "value": [
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": "P1",
                    "DeletedDateTime": "2024-01-15T10:30:00Z",
                },
                {
                    "ResourceName": "Member",
                    "ResourceRecordKey": "M1",
                    "DeletedDateTime": "2024-01-15T10:45:00Z",
                },
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.monitor_deletion_activity(
            hours_back=12, alert_threshold=50
        )

        assert "@odata.context" in result
        assert result["@odata.context"] == "Deletion monitoring"
        assert "summary" in result
        assert "alerts" in result
        assert "status" in result

        summary = result["summary"]
        assert summary["total_deletions"] == 2
        assert result["monitoring_period"] == "12 hours"
        assert result["status"] == "NORMAL"  # Below threshold
        assert len(result["alerts"]) == 0  # No alerts for low volume

    @responses.activate
    def test_monitor_deletion_activity_high_volume(self) -> None:
        """Test monitor deletion activity with high volume triggering alerts."""
        # Create a large number of deletion records
        mock_records = []
        for i in range(150):  # Above threshold of 100
            mock_records.append(
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": f"P{i}",
                    "DeletedDateTime": "2024-01-15T10:30:00Z",
                }
            )

        mock_response = {"value": mock_records}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.monitor_deletion_activity(alert_threshold=100)

        summary = result["summary"]
        assert summary["total_deletions"] == 150
        assert result["status"] == "ALERT"  # Above threshold
        assert len(result["alerts"]) > 0  # Should have alerts

    @responses.activate
    def test_monitor_deletion_activity_concentrated_activity(self) -> None:
        """Test monitor deletion activity with concentrated resource activity."""
        # Create records heavily concentrated on one resource type
        mock_records = []
        for i in range(90):  # 90% of one type
            mock_records.append(
                {
                    "ResourceName": "Property",
                    "ResourceRecordKey": f"P{i}",
                    "DeletedDateTime": "2024-01-15T10:30:00Z",
                }
            )
        for i in range(10):  # 10% of another type
            mock_records.append(
                {
                    "ResourceName": "Member",
                    "ResourceRecordKey": f"M{i}",
                    "DeletedDateTime": "2024-01-15T10:30:00Z",
                }
            )

        mock_response = {"value": mock_records}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.monitor_deletion_activity()

        summary = result["summary"]
        assert summary["total_deletions"] == 100
        assert result["status"] == "ALERT"  # Above default threshold
        assert len(result["alerts"]) > 0  # Should have alerts due to volume

    @responses.activate
    def test_top_limit_enforcement(self) -> None:
        """Test that top parameter is limited to 200."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        # Request more than 200 records
        result = self.client.get_deleted(top=500)

        assert result == mock_response
        request = responses.calls[0].request
        # Should be capped at 200
        assert request.url is not None and "%24top=200" in request.url

    @responses.activate
    def test_select_list_parameter(self) -> None:
        """Test select parameter with list input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(
            select=["ResourceName", "ResourceRecordKey", "DeletedDateTime"]
        )

        assert result == mock_response
        request = responses.calls[0].request
        assert "ResourceName" in request.url
        assert "ResourceRecordKey" in request.url
        assert "DeletedDateTime" in request.url

    @responses.activate
    def test_select_string_parameter(self) -> None:
        """Test select parameter with string input."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted(select="ResourceName,DeletedDateTime")

        assert result == mock_response
        request = responses.calls[0].request
        assert "ResourceName" in request.url
        assert "DeletedDateTime" in request.url

    @responses.activate
    def test_deleted_not_found(self) -> None:
        """Test deleted records not found error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json={"error": {"message": "Resource not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found"):
            self.client.get_deleted(filter_query="ResourceName eq 'NonExistent'")

    def test_resource_name_enum_values(self) -> None:
        """Test ResourceName enum values are correct."""
        assert ResourceName.PROPERTY.value == "Property"
        assert ResourceName.MEMBER.value == "Member"
        assert ResourceName.OFFICE.value == "Office"
        assert ResourceName.OPENHOUSE.value == "OpenHouse"
        assert ResourceName.MEDIA.value == "Media"
        assert ResourceName.HISTORY_TRANSACTIONAL.value == "HistoryTransactional"
        assert (
            ResourceName.PROPERTY_GREEN_VERIFICATION.value
            == "PropertyGreenVerification"
        )
        assert ResourceName.PROPERTY_UNIT_TYPES.value == "PropertyUnitTypes"
        assert ResourceName.ADU.value == "Adu"

    @responses.activate
    def test_combined_filters(self) -> None:
        """Test combining resource filter with additional filters."""
        mock_response = {"@odata.context": "test", "value": []}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/Deleted",
            json=mock_response,
            status=200,
        )

        result = self.client.get_deleted_by_resource(
            resource_name=ResourceName.PROPERTY,
            filter_query="DeletedDateTime gt 2024-01-01T00:00:00Z",
        )

        assert result == mock_response
        request = responses.calls[0].request
        # Should contain both filters combined with 'and'
        assert "ResourceName" in request.url
        assert "Property" in request.url
        assert "DeletedDateTime" in request.url
