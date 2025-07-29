"""Tests for main WFRMLS client."""

import pytest
import responses

from wfrmls.client import WFRMLSClient
from wfrmls.exceptions import WFRMLSError


class TestWFRMLSClientInit:
    """Test WFRMLSClient initialization."""

    def test_init_with_bearer_token(self) -> None:
        """Test initialization with provided bearer token."""
        client = WFRMLSClient(bearer_token="test_token")
        assert client._bearer_token == "test_token"

    def test_init_with_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = WFRMLSClient(
            bearer_token="test_token", 
            base_url="https://custom.api.com"
        )
        assert client._base_url == "https://custom.api.com"

    def test_init_defaults(self) -> None:
        """Test initialization with defaults."""
        client = WFRMLSClient(bearer_token="test_token")
        assert client._bearer_token == "test_token"
        assert client._base_url is None
        # Verify lazy initialization - clients should be None initially
        assert client._property is None
        assert client._member is None
        assert client._office is None


class TestWFRMLSClient:
    """Test WFRMLSClient main functionality."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = WFRMLSClient(bearer_token="test_bearer_token")

    def test_property_client_lazy_initialization(self) -> None:
        """Test that property client is lazily initialized."""
        assert self.client._property is None
        property_client = self.client.property
        assert self.client._property is not None
        assert property_client is self.client._property
        # Second access should return same instance
        assert self.client.property is property_client

    def test_member_client_lazy_initialization(self) -> None:
        """Test that member client is lazily initialized."""
        assert self.client._member is None
        member_client = self.client.member
        assert self.client._member is not None
        assert member_client is self.client._member

    def test_office_client_lazy_initialization(self) -> None:
        """Test that office client is lazily initialized."""
        assert self.client._office is None
        office_client = self.client.office
        assert self.client._office is not None
        assert office_client is self.client._office

    def test_openhouse_client_lazy_initialization(self) -> None:
        """Test that openhouse client is lazily initialized."""
        assert self.client._openhouse is None
        openhouse_client = self.client.openhouse
        assert self.client._openhouse is not None
        assert openhouse_client is self.client._openhouse



    def test_data_system_client_lazy_initialization(self) -> None:
        """Test that data system client is lazily initialized."""
        assert self.client._data_system is None
        data_client = self.client.data_system
        assert self.client._data_system is not None
        assert data_client is self.client._data_system

    def test_resource_client_lazy_initialization(self) -> None:
        """Test that resource client is lazily initialized."""
        assert self.client._resource is None
        resource_client = self.client.resource
        assert self.client._resource is not None
        assert resource_client is self.client._resource

    def test_property_unit_types_client_lazy_initialization(self) -> None:
        """Test that property unit types client is lazily initialized."""
        assert self.client._property_unit_types is None
        unit_types_client = self.client.property_unit_types
        assert self.client._property_unit_types is not None
        assert unit_types_client is self.client._property_unit_types

    def test_lookup_client_lazy_initialization(self) -> None:
        """Test that lookup client is lazily initialized."""
        assert self.client._lookup is None
        lookup_client = self.client.lookup
        assert self.client._lookup is not None
        assert lookup_client is self.client._lookup

    def test_adu_client_lazy_initialization(self) -> None:
        """Test that ADU client is lazily initialized."""
        assert self.client._adu is None
        adu_client = self.client.adu
        assert self.client._adu is not None
        assert adu_client is self.client._adu

    def test_deleted_client_lazy_initialization(self) -> None:
        """Test that deleted client is lazily initialized."""
        assert self.client._deleted is None
        deleted_client = self.client.deleted
        assert self.client._deleted is not None
        assert deleted_client is self.client._deleted

    @responses.activate
    def test_get_service_document_success(self) -> None:
        """Test successful service document retrieval."""
        mock_response = {
            "@odata.context": "https://resoapi.utahrealestate.com/reso/odata/$metadata",
            "value": [
                {"name": "Property", "url": "Property"},
                {"name": "Member", "url": "Member"},
                {"name": "Office", "url": "Office"}
            ]
        }

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/",
            json=mock_response,
            status=200,
        )

        result = self.client.get_service_document()
        assert result == mock_response
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_service_document_error(self) -> None:
        """Test service document retrieval error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/",
            json={"error": {"message": "Service unavailable"}},
            status=500,
        )

        with pytest.raises(WFRMLSError):
            self.client.get_service_document()

    @responses.activate
    def test_get_metadata_success(self) -> None:
        """Test successful metadata retrieval."""
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
            <edmx:DataServices>
                <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm">
                    <EntityType Name="Property">
                        <Key>
                            <PropertyRef Name="ListingKey"/>
                        </Key>
                    </EntityType>
                </Schema>
            </edmx:DataServices>
        </edmx:Edmx>"""

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/$metadata",
            body=mock_xml,
            status=200,
            content_type="application/xml"
        )

        result = self.client.get_metadata()
        assert "edmx:Edmx" in result
        assert "EntityType" in result
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_metadata_error(self) -> None:
        """Test metadata retrieval error."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/$metadata",
            body="Error occurred",
            status=500,
        )

        with pytest.raises(WFRMLSError, match="Failed to fetch metadata: 500"):
            self.client.get_metadata()

    def test_all_client_properties_accessible(self) -> None:
        """Test that all available client properties are accessible."""
        # This tests that the property decorators work correctly
        # NOTE: Media, History, and Green Verification clients are disabled
        clients = [
            self.client.property,
            self.client.member, 
            self.client.office,
            self.client.openhouse,
            self.client.data_system,
            self.client.resource,
            self.client.property_unit_types,
            self.client.lookup,
            self.client.adu,
            self.client.deleted
        ]
        
        # All should be instantiated now
        for client in clients:
            assert client is not None
            assert hasattr(client, 'bearer_token')
            assert client.bearer_token == "test_bearer_token"

    def test_client_tokens_propagated(self) -> None:
        """Test that bearer tokens are properly propagated to sub-clients."""
        custom_token = "custom_test_token"
        custom_url = "https://custom.api.com"
        
        client = WFRMLSClient(bearer_token=custom_token, base_url=custom_url)
        
        # Access a few clients to verify token/URL propagation
        assert client.property.bearer_token == custom_token
        assert client.property.base_url == custom_url
        assert client.member.bearer_token == custom_token
        assert client.member.base_url == custom_url
        assert client.deleted.bearer_token == custom_token
        assert client.deleted.base_url == custom_url 